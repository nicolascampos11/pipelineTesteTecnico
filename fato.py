
import csv
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "Contas Medicas.txt"
MAPA_PROCEDIMENTO = Path(__file__).parent.parent / "data" / "processed" / "mapa_procedimento.csv"
MAPA_TEMPO = Path(__file__).parent.parent / "data" / "processed" / "mapa_tempo.csv"
OUT_PATH = Path(__file__).parent.parent / "data" / "processed" / "fato_contas_medicas.csv"


def carregar_mapa_procedimento() -> dict:
    mapa = {}
    with open(MAPA_PROCEDIMENTO, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapa[row["descricao_original_lower"]] = row["id_procedimento"]
    return mapa


def carregar_mapa_tempo() -> dict:
    mapa = {}
    with open(MAPA_TEMPO, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapa[row["dt_competencia"]] = row["id_tempo"]
    return mapa


def normalizar_procedimento(texto: str) -> str:
    return texto.replace("\t", " ").strip().strip('"').strip().lower()


def montar():
    mapa_procedimento = carregar_mapa_procedimento()
    mapa_tempo = carregar_mapa_tempo()

    total_linhas = 0
    procedimentos_nao_mapeados = 0
    tempos_nao_mapeados = 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(RAW_PATH, encoding="utf-8-sig") as f_in, \
         open(OUT_PATH, "w", newline="", encoding="utf-8") as f_out:

        reader = csv.DictReader(f_in, delimiter=";")
        writer = csv.DictWriter(f_out, fieldnames=[
            "id_conta_medica", "id_tempo", "cd_pessoa", "id_empresa",
            "id_operadora", "cnpj_prestador", "id_procedimento", "qtd", "valor",
        ])
        writer.writeheader()

        for row in reader:
            total_linhas += 1

            chave_procedimento = normalizar_procedimento(row["PROCEDIMENTO"])
            id_procedimento = mapa_procedimento.get(chave_procedimento)
            if id_procedimento is None:
                procedimentos_nao_mapeados += 1

            id_tempo = mapa_tempo.get(row["DT_COMPETENCIA"])
            if id_tempo is None:
                tempos_nao_mapeados += 1

            valor = round(float(row["VALOR"].replace(",", ".")), 2)
            qtd = int(row["QTD"])

            writer.writerow({
                "id_conta_medica": row["ID_CONTA_MEDICA"],
                "id_tempo": id_tempo,
                "cd_pessoa": row["CD_PESSOA"],
                "id_empresa": row["ID_EMPRESA"],
                "id_operadora": row["ID_OPERADORA"],
                "cnpj_prestador": row["CNPJ_PRESTADOR"],
                "id_procedimento": id_procedimento,
                "qtd": qtd,
                "valor": valor,
            })

            if total_linhas % 1_000_000 == 0:
                print(f"Progresso: {total_linhas:,} linhas processadas".replace(",", "."))

    print(f"\nTotal de linhas processadas: {total_linhas}")
    print(f"Procedimentos não mapeados: {procedimentos_nao_mapeados}")
    print(f"Tempos não mapeados: {tempos_nao_mapeados}")
    print(f"Fato gerada em: {OUT_PATH}")


if __name__ == "__main__":
    montar()