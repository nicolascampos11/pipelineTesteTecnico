SELECT * FROM pg_stat_progress_copy;

1
SELECT DISTINCT cidade FROM dim_prestador
WHERE cidade ILIKE '%paulo%' OR cidade ILIKE '%janeiro%' OR cidade ILIKE '%niter%';

SELECT
    dt.ano,
    dp.cidade,
    ROUND(SUM(f.valor), 2) AS valor_total
FROM fato_contas_medicas f
JOIN dim_tempo dt ON f.id_tempo = dt.id_tempo
JOIN dim_prestador dp ON f.cnpj_prestador = dp.cnpj
WHERE dt.ano IN (2023, 2024)
  AND dp.cidade IN ('SAO PAULO', 'RIO DE JANEIRO', 'NITEROI')
GROUP BY dt.ano, dp.cidade
ORDER BY dt.ano, dp.cidade;

.............................
2
with ranking as (
	SELECT
        dt.ano,
        dpr.descricao,
        ROUND(SUM(f.valor), 2) AS valor_total,
        ROW_NUMBER() OVER (PARTITION BY dt.ano ORDER BY SUM(f.valor) DESC) AS posicao
    FROM fato_contas_medicas f
    JOIN dim_tempo dt ON f.id_tempo = dt.id_tempo
    JOIN dim_prestador dp ON f.cnpj_prestador = dp.cnpj
    JOIN dim_procedimento dpr ON f.id_procedimento = dpr.id_procedimento
    WHERE dt.ano IN (2023, 2024)
      AND dp.cidade IN ('SAO PAULO', 'RIO DE JANEIRO', 'NITEROI')
    GROUP BY dt.ano, dpr.descricao
)
SELECT
    posicao,
    MAX(CASE WHEN ano = 2023 THEN descricao END) AS procedimento_2023,
    MAX(CASE WHEN ano = 2023 THEN valor_total END) AS valor_2023,
    MAX(CASE WHEN ano = 2024 THEN descricao END) AS procedimento_2024,
    MAX(CASE WHEN ano = 2024 THEN valor_total END) AS valor_2024
FROM ranking
WHERE posicao <= 10
GROUP BY posicao
ORDER BY posicao;

.............................

3
a
WITH ranking_faixa AS (
    SELECT
        dt.ano,
        dpe.faixa_etaria,
        ROUND(SUM(f.valor), 2) AS valor_total,
        ROW_NUMBER() OVER (PARTITION BY dt.ano ORDER BY SUM(f.valor) DESC) AS posicao
    FROM fato_contas_medicas f
    JOIN dim_tempo dt ON f.id_tempo = dt.id_tempo
    JOIN dim_pessoa dpe ON f.cd_pessoa = dpe.codigo_pessoa
    WHERE dt.ano IN (2023, 2024)
    GROUP BY dt.ano, dpe.faixa_etaria
)
SELECT ano, faixa_etaria, valor_total
FROM ranking_faixa
WHERE posicao = 1
ORDER BY ano;

b
SELECT
    dt.ano,
    dp.cidade,
    dp.estado,
    COUNT(DISTINCT dpe.codigo_pessoa) AS qtd_pessoas
FROM fato_contas_medicas f
JOIN dim_tempo dt ON f.id_tempo = dt.id_tempo
JOIN dim_pessoa dpe ON f.cd_pessoa = dpe.codigo_pessoa
JOIN dim_prestador dp ON f.cnpj_prestador = dp.cnpj
WHERE dt.ano IN (2023, 2024)
  AND dpe.faixa_etaria = '59 anos ou mais'
GROUP BY dt.ano, dp.cidade, dp.estado
ORDER BY dt.ano, qtd_pessoas DESC
LIMIT 20;

.............................

4
WITH totais_ano AS (
    SELECT
        dt.ano,
        COUNT(DISTINCT dpe.codigo_pessoa) AS total_pessoas,
        SUM(f.valor) AS total_valor
    FROM fato_contas_medicas f
    JOIN dim_tempo dt ON f.id_tempo = dt.id_tempo
    JOIN dim_pessoa dpe ON f.cd_pessoa = dpe.codigo_pessoa
    WHERE dt.ano IN (2023, 2024)
    GROUP BY dt.ano
),
faixa_idosa AS (
    SELECT
        dt.ano,
        COUNT(DISTINCT dpe.codigo_pessoa) AS pessoas_59,
        SUM(f.valor) AS valor_59
    FROM fato_contas_medicas f
    JOIN dim_tempo dt ON f.id_tempo = dt.id_tempo
    JOIN dim_pessoa dpe ON f.cd_pessoa = dpe.codigo_pessoa
    WHERE dt.ano IN (2023, 2024)
      AND dpe.faixa_etaria = '59 anos ou mais'
    GROUP BY dt.ano
)
SELECT
    t.ano,
    fIdo.pessoas_59,
    t.total_pessoas,
    ROUND(fIdo.pessoas_59 * 100.0 / t.total_pessoas, 2) AS pct_pessoas,
    ROUND(fIdo.valor_59, 2) AS valor_59,
    ROUND(t.total_valor, 2) AS total_valor,
    ROUND(fIdo.valor_59 * 100.0 / t.total_valor, 2) AS pct_valor
FROM totais_ano t
JOIN faixa_idosa fIdo ON t.ano = fIdo.ano
ORDER BY t.ano;

.............................

5
WITH distribuicao AS (
    SELECT
        dt.ano,
        de.empresa,
        dpe.sexo,
        COUNT(DISTINCT dpe.codigo_pessoa) AS qtd_pessoas
    FROM fato_contas_medicas f
    JOIN dim_tempo dt ON f.id_tempo = dt.id_tempo
    JOIN dim_pessoa dpe ON f.cd_pessoa = dpe.codigo_pessoa
    JOIN dim_empresa de ON f.id_empresa = de.cd_empresa
    WHERE dt.ano IN (2023, 2024)
      AND dpe.faixa_etaria = '59 anos ou mais'
    GROUP BY dt.ano, de.empresa, dpe.sexo
),
totais_empresa AS (
    SELECT ano, empresa, SUM(qtd_pessoas) AS total_empresa
    FROM distribuicao
    GROUP BY ano, empresa
)
SELECT
    d.ano,
    d.empresa,
    te.total_empresa,
    d.sexo,
    d.qtd_pessoas,
    ROUND(d.qtd_pessoas * 100.0 / te.total_empresa, 2) AS percentual_na_empresa
FROM distribuicao d
JOIN totais_empresa te ON d.ano = te.ano AND d.empresa = te.empresa
ORDER BY d.ano, te.total_empresa DESC, d.sexo;