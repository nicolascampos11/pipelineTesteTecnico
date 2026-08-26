import csv
from datetime import datetime
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "Contas Medicas.txt"
OUT_DIM = Path(__file__).parent.parent / "data" / "processed" / "dim_tempo.csv"
OUT_MAPA = Path(__file__).parent.parent / "data" / "processed" / "mapa_tempo.csv"

NOMES_MES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def gerar():
    competencias = set()
    total_linhas = 0

    with open(RAW_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            total_linhas += 1
            competencias.add(row["DT_COMPETENCIA"])

    competencias_ordenadas = sorted(
        competencias, key=lambda d: datetime.strptime(d, "%d/%m/%Y")
    )

    linhas_dim = []
    id_por_competencia = {}

    for i, dt_str in enumerate(competencias_ordenadas, start=1):
        dt = datetime.strptime(dt_str, "%d/%m/%Y")
        ano = dt.year
        mes = dt.month
        trimestre = (mes - 1) // 3 + 1

        id_por_competencia[dt_str] = i
        linhas_dim.append({
            "id_tempo": i,
            "dt_competencia": dt_str,
            "ano": ano,
            "mes": mes,
            "nome_mes": NOMES_MES[mes - 1],
            "trimestre": trimestre,
        })

    OUT_DIM.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIM, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id_tempo", "dt_competencia", "ano", "mes", "nome_mes", "trimestre"]
        )
        writer.writeheader()
        writer.writerows(linhas_dim)

    with open(OUT_MAPA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["dt_competencia", "id_tempo"])
        writer.writeheader()
        for dt_str, id_tempo in id_por_competencia.items():
            writer.writerow({"dt_competencia": dt_str, "id_tempo": id_tempo})

    print(f"Linhas lidas na base fato: {total_linhas}")
    print(f"Competências distintas: {len(linhas_dim)}")
    print(f"Dim_Tempo gerada em: {OUT_DIM}")
    print(f"Mapa de apoio gerado em: {OUT_MAPA}")


if __name__ == "__main__":
    gerar()
