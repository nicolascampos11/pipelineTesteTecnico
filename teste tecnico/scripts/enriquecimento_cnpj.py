import csv
import json
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

IN_PATH = Path(__file__).parent.parent / "data" / "processed" / "cnpjs_prioritarios.csv"
OUT_PATH = Path(__file__).parent.parent / "data" / "processed" / "dim_prestador.csv"
CACHE_PATH = Path(__file__).parent.parent / "cache" / "cache_cnpj.json"
cache_lock = threading.Lock()

MAX_WORKERS = 6
MAX_TENTATIVAS = 4
TIMEOUT = 10


def carregar_cache() -> dict:
    if CACHE_PATH.exists():
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_cache(cache: dict):
    with cache_lock:
        snapshot = dict(cache)

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = CACHE_PATH.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False)
    temp_path.replace(CACHE_PATH)


def consultar_cnpj(cnpj: str) -> dict:
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resp = requests.get(
                f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}", timeout=TIMEOUT
            )
            if resp.status_code == 200:
                dados = resp.json()
                return {
                    "cnpj": cnpj,
                    "cep": dados.get("cep"),
                    "cidade": dados.get("municipio"),
                    "estado": dados.get("uf"),
                    "status": "ok",
                }
            if resp.status_code == 429:
                time.sleep(2 ** tentativa)
                continue
            if resp.status_code == 404:
                return {"cnpj": cnpj, "cep": None, "cidade": None, "estado": None,
                         "status": "nao_encontrado"}
            time.sleep(1 * tentativa)
        except requests.RequestException:
            time.sleep(1 * tentativa)

    return {"cnpj": cnpj, "cep": None, "cidade": None, "estado": None, "status": "erro"}


def consultar_cep_fallback(cep: str) -> dict:
    try:
        resp = requests.get(f"https://brasilapi.com.br/api/cep/v1/{cep}", timeout=TIMEOUT)
        if resp.status_code == 200:
            dados = resp.json()
            return {"cidade": dados.get("city"), "estado": dados.get("state")}
    except requests.RequestException:
        pass
    return {"cidade": None, "estado": None}


def enriquecer_um(cnpj: str, cache: dict) -> dict:
    with cache_lock:
        if cnpj in cache:
            return cache[cnpj]

    resultado = consultar_cnpj(cnpj)

    if resultado["status"] == "ok" and (not resultado["cidade"] or not resultado["estado"]) and resultado["cep"]:
        fallback = consultar_cep_fallback(resultado["cep"])
        resultado["cidade"] = resultado["cidade"] or fallback["cidade"]
        resultado["estado"] = resultado["estado"] or fallback["estado"]

    with cache_lock:
        cache[cnpj] = resultado
    return resultado


def main():
    with open(IN_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cnpjs = [row["CNPJ_PRESTADOR"] for row in reader]

    cache = carregar_cache()
    ja_em_cache = sum(1 for c in cnpjs if c in cache)
    print(f"Total de CNPJs: {len(cnpjs)} | já em cache: {ja_em_cache}")

    pendentes = [c for c in cnpjs if c not in cache]
    processados = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(enriquecer_um, cnpj, cache): cnpj for cnpj in pendentes}

        for future in as_completed(futures):
            future.result()
            processados += 1

            if processados % 500 == 0:
                salvar_cache(cache)
                print(f"Progresso: {processados}/{len(pendentes)}")

    salvar_cache(cache)

    linhas = [cache[c] for c in cnpjs]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cnpj", "cep", "cidade", "estado", "status"])
        writer.writeheader()
        writer.writerows(linhas)

    nao_enriquecidos = sum(1 for l in linhas if l["status"] != "ok")
    print(f"\nConcluído. {len(linhas)} prestadores no total.")
    print(f"Não enriquecidos: {nao_enriquecidos} ({nao_enriquecidos / len(linhas) * 100:.2f}%)")
    print(f"Arquivo gerado em: {OUT_PATH}")


if __name__ == "__main__":
    main()
