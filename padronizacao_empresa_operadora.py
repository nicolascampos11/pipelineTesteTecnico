import csv
from pathlib import Path

RAW_EMPRESAS = Path(__file__).parent.parent / "data" / "raw" / "Cadastro de empresas.csv"
RAW_OPERADORAS = Path(__file__).parent.parent / "data" / "raw" / "Cadastro de operadoras.csv"

OUT_EMPRESA = Path(__file__).parent.parent / "data" / "processed" / "dim_empresa.csv"
OUT_OPERADORA = Path(__file__).parent.parent / "data" / "processed" / "dim_operadora.csv"


def gerar_dim_empresa():
    with open(RAW_EMPRESAS, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        linhas = [
            {
                "cd_empresa": row["CD_EMPRESA"],
                "cnpj_empresa": row["CNPJ_EMPRESA"],
                "empresa": row["EMPRESA"],
            }
            for row in reader
        ]

    OUT_EMPRESA.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_EMPRESA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cd_empresa", "cnpj_empresa", "empresa"])
        writer.writeheader()
        writer.writerows(linhas)

    print(f"Dim_Empresa: {len(linhas)} registros -> {OUT_EMPRESA}")


def gerar_dim_operadora():
    with open(RAW_OPERADORAS, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        linhas = [
            {
                "cd_operadora": row["CD_OPERADORA"],
                "operadora": row["OPERADORA"],
            }
            for row in reader
        ]

    OUT_OPERADORA.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_OPERADORA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cd_operadora", "operadora"])
        writer.writeheader()
        writer.writerows(linhas)

    print(f"Dim_Operadora: {len(linhas)} registros -> {OUT_OPERADORA}")


if __name__ == "__main__":
    gerar_dim_empresa()
    gerar_dim_operadora()