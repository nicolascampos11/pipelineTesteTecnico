import pandas as pd
from pathlib import Path

PROCESSED = Path(__file__).parent.parent / "data" / "processed"

ARQUIVOS = [
    "dim_pessoa.csv",
    "dim_empresa.csv",
    "dim_operadora.csv",
    "dim_procedimento.csv",
    "dim_tempo.csv",
    "dim_prestador.csv",
    "fato_contas_medicas.csv",
]


def converter():
    for nome in ARQUIVOS:
        caminho_csv = PROCESSED / nome
        if not caminho_csv.exists():
            print(f"AVISO: {nome} não encontrado, pulando.")
            continue

        df = pd.read_csv(caminho_csv)
        caminho_parquet = caminho_csv.with_suffix(".parquet")
        df.to_parquet(caminho_parquet, index=False)

        tamanho_csv = caminho_csv.stat().st_size / (1024 * 1024)
        tamanho_parquet = caminho_parquet.stat().st_size / (1024 * 1024)
        print(f"{nome}: {len(df):,} linhas | {tamanho_csv:.1f} MB -> {tamanho_parquet:.1f} MB")


if __name__ == "__main__":
    converter()
