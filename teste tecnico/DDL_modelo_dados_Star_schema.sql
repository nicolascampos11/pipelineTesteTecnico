-- DDL do Star Schema para PostgreSQL

CREATE TABLE dim_pessoa (
    codigo_pessoa VARCHAR(64) PRIMARY KEY,
    dt_nascimento VARCHAR(10),
    sexo VARCHAR(20),
    idade_atual INT NULL,
    faixa_etaria VARCHAR(30)
);

CREATE TABLE dim_empresa (
    cd_empresa INT PRIMARY KEY,
    cnpj_empresa VARCHAR(20),
    empresa VARCHAR(255)
);

CREATE TABLE dim_operadora (
    cd_operadora INT PRIMARY KEY,
    operadora VARCHAR(255)
);

CREATE TABLE dim_procedimento (
    id_procedimento INT PRIMARY KEY,
    descricao VARCHAR(500)
);

CREATE TABLE dim_tempo (
    id_tempo INT PRIMARY KEY,
    dt_competencia VARCHAR(10),
    ano INT,
    mes INT,
    nome_mes VARCHAR(20),
    trimestre INT
);

CREATE TABLE dim_prestador (
    cnpj VARCHAR(20) PRIMARY KEY,
    cep VARCHAR(10),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    status VARCHAR(20)
);

CREATE TABLE fato_contas_medicas (
    id_linha BIGSERIAL PRIMARY KEY,
    id_conta_medica VARCHAR(64),
    id_tempo INT REFERENCES dim_tempo(id_tempo),
    cd_pessoa VARCHAR(64) REFERENCES dim_pessoa(codigo_pessoa),
    id_empresa INT REFERENCES dim_empresa(cd_empresa),
    id_operadora INT REFERENCES dim_operadora(cd_operadora),
    cnpj_prestador VARCHAR(20) REFERENCES dim_prestador(cnpj),
    id_procedimento INT REFERENCES dim_procedimento(id_procedimento),
    qtd INT,
    valor DECIMAL(14,2)
);

CREATE INDEX idx_fato_tempo ON fato_contas_medicas(id_tempo);
CREATE INDEX idx_fato_pessoa ON fato_contas_medicas(cd_pessoa);
CREATE INDEX idx_fato_prestador ON fato_contas_medicas(cnpj_prestador);
CREATE INDEX idx_fato_procedimento ON fato_contas_medicas(id_procedimento);
