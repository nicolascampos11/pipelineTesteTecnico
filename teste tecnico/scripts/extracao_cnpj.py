import csv
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "Contas Medicas.txt"
OUT_PATH = Path(__file__).parent.parent / "data" / "processed" / "cnpjs_distintos.csv"


def extrair():
    cnpjs = set()
    total_linhas = 0

    with open(RAW_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            total_linhas += 1
            cnpj = row["CNPJ_PRESTADOR"].strip()
            if cnpj:
                cnpjs.add(cnpj)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["CNPJ_PRESTADOR"])
        for cnpj in sorted(cnpjs):
            writer.writerow([cnpj])

    print(f"Linhas lidas na base fato: {total_linhas}")
    print(f"CNPJs distintos: {len(cnpjs)}")
    print(f"Arquivo gerado em: {OUT_PATH}")


if __name__ == "__main__":
    extrair()
