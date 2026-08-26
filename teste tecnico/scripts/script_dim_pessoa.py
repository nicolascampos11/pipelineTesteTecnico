import csv
from datetime import date, datetime
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "Cadastro de pessoas.csv"
OUT_PATH = Path(__file__).parent.parent / "data" / "processed" / "dim_pessoa.csv"

DATAS_LIMITE = {"01/01/1900", "31/12/9999"}
IDADE_MAX = 120

FAIXAS = [
    (0, 18, "0 a 18 anos"),
    (19, 23, "19 a 23 anos"),
    (24, 28, "24 a 28 anos"),
    (29, 33, "29 a 33 anos"),
    (34, 38, "34 a 38 anos"),
    (39, 43, "39 a 43 anos"),
    (44, 48, "44 a 48 anos"),
    (49, 53, "49 a 53 anos"),
    (54, 58, "54 a 58 anos"),
]
FAIXA_DEFAULT = "59 anos ou mais"
FAIXA_NAO_INFORMADO = "Não informado"

def calcular_idade(data_nascimento: date, hoje: date) -> int:
    idade = hoje.year - data_nascimento.year
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return idade

def calculo_faixa_etaria(idade: int) -> str:
    for minimo, maximo, rotulo in FAIXAS:
        if minimo <= idade <= maximo:
            return rotulo
    return FAIXA_DEFAULT

def processar():
    hoje = date.today()
    total = 0
    sem_informacao = 0
    linhas_saida = []

    with open(RAW_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            total += 1
            codigo = row["CODIGO_PESSOA"]
            sexo = row["SEXO"]
            dt_str = (row["DT_NASCIMENTO"] or "").strip()

            if not dt_str or dt_str in DATAS_LIMITE:
                sem_informacao += 1
                linhas_saida.append({
                    "CODIGO_PESSOA": codigo,
                    "DT_NASCIMENTO": dt_str or "",
                    "SEXO": sexo,
                    "IDADE_ATUAL": "",
                    "FAIXA_ETARIA": FAIXA_NAO_INFORMADO,
                })
                continue

            dt_nasc = datetime.strptime(dt_str, "%d/%m/%Y").date()
            idade = calcular_idade(dt_nasc, hoje)

            if idade < 0 or idade > IDADE_MAX:
                sem_informacao += 1
                linhas_saida.append({
                    "CODIGO_PESSOA": codigo,
                    "DT_NASCIMENTO": dt_str,
                    "SEXO": sexo,
                    "IDADE_ATUAL": "",
                    "FAIXA_ETARIA": FAIXA_NAO_INFORMADO,
                })
                continue

            faixa = calculo_faixa_etaria(idade)

            linhas_saida.append({
                "CODIGO_PESSOA": codigo,
                "DT_NASCIMENTO": dt_str,
                "SEXO": sexo,
                "IDADE_ATUAL": idade,
                "FAIXA_ETARIA": faixa,
            })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["CODIGO_PESSOA", "DT_NASCIMENTO", "SEXO", "IDADE_ATUAL", "FAIXA_ETARIA"],
        )
        writer.writeheader()
        writer.writerows(linhas_saida)

    print(f"Total processado: {total}")
    print(f"Sem informação de nascimento: {sem_informacao} "
          f"({sem_informacao / total * 100:.2f}%)")
    print(f"Arquivo gerado em: {OUT_PATH}")


if __name__ == "__main__":
    processar()
