import csv
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "Contas Medicas.txt"
OUT_DIM = Path(__file__).parent.parent / "data" / "processed" / "dim_procedimento.csv"
OUT_MAPA = Path(__file__).parent.parent / "data" / "processed" / "mapa_procedimento.csv"


def gerar():
    descricao_por_chave = {}   
    total_linhas = 0

    with open(RAW_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            total_linhas += 1
            proc = row["PROCEDIMENTO"].replace("\t", " ").strip().strip('"').strip()
            chave = proc.lower()

            if chave not in descricao_por_chave:
                descricao_por_chave[chave] = proc

    chaves_ordenadas = sorted(descricao_por_chave.keys())

    linhas_dim = []
    id_por_chave = {}
    for i, chave in enumerate(chaves_ordenadas, start=1):
        id_por_chave[chave] = i
        linhas_dim.append({
            "id_procedimento": i,
            "descricao": descricao_por_chave[chave],
        })

    OUT_DIM.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIM, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id_procedimento", "descricao"])
        writer.writeheader()
        writer.writerows(linhas_dim)

    with open(OUT_MAPA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["descricao_original_lower", "id_procedimento"])
        writer.writeheader()
        for chave, id_proc in id_por_chave.items():
            writer.writerow({"descricao_original_lower": chave, "id_procedimento": id_proc})

    print(f"Linhas lidas na base fato: {total_linhas}")
    print(f"Procedimentos distintos: {len(linhas_dim)}")
    print(f"Dim_Procedimento gerada em: {OUT_DIM}")
    print(f"Mapa de apoio gerado em: {OUT_MAPA}")


if __name__ == "__main__":
    gerar()
