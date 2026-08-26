
import csv
import json
from pathlib import Path

CNPJS_TODOS = Path(__file__).parent.parent / "data" / "processed" / "cnpjs_distintos.csv"
CACHE_PATH = Path(__file__).parent.parent / "cache" / "cache_cnpj.json"
OUT_DIM = Path(__file__).parent.parent / "data" / "processed" / "dim_prestador.csv"


def montar():
    with open(CACHE_PATH, encoding="utf-8") as f:
        cache = json.load(f)

    with open(CNPJS_TODOS, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        todos_cnpjs = [row["CNPJ_PRESTADOR"] for row in reader]

    linhas = []
    enriquecidos = 0
    nao_processados = 0

    for cnpj in todos_cnpjs:
        if cnpj in cache:
            r = cache[cnpj]
            if r["status"] == "ok":
                enriquecidos += 1
            linhas.append({
                "cnpj": cnpj,
                "cep": r.get("cep") or "",
                "cidade": r.get("cidade") or "",
                "estado": r.get("estado") or "",
                "status": r["status"],
            })
        else:
            nao_processados += 1
            linhas.append({
                "cnpj": cnpj,
                "cep": "",
                "cidade": "",
                "estado": "",
                "status": "nao_processado",
            })

    OUT_DIM.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIM, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cnpj", "cep", "cidade", "estado", "status"])
        writer.writeheader()
        writer.writerows(linhas)

    print(f"Total de CNPJs na Dim_Prestador: {len(linhas)}")
    print(f"Enriquecidos com sucesso (status=ok): {enriquecidos} ({enriquecidos/len(linhas)*100:.1f}%)")
    print(f"Não processados (rate limit / não priorizados): {nao_processados} ({nao_processados/len(linhas)*100:.1f}%)")
    print(f"Dim_Prestador final gerada em: {OUT_DIM}")


if __name__ == "__main__":
    montar()
