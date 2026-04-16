CREATE TABLE teste.tabela_geral_consolidada AS
SELECT 
    -- 1. Dados de Produção
    p.data,
    p.municipio AS codigo_ibge,
    p.ind01_num_prim_consulta,
    p.ind02_num_trat_concluido,
    p.ind02_den_prim_consulta,
    p.ind03_num_exodontias,
    p.ind03_den_total_clinicos,
    p.ind04_num_escovacao_6_12,
    p.ind05_num_preventivos,
    p.ind05_den_total_individuais,
    p.ind06_num_tra_art,
    p.ind06_den_restauradores,

    -- 2. Colunas de Tempo calculadas
    EXTRACT(YEAR FROM p.data) AS ano,
    CASE 
        WHEN EXTRACT(MONTH FROM p.data) BETWEEN 1 AND 4 THEN 1
        WHEN EXTRACT(MONTH FROM p.data) BETWEEN 5 AND 8 THEN 2
        ELSE 3
    END AS quadrimestre,

    -- 3. Informações Geográficas (da sua tabela municipios_ms)
    m.nome_municipio,
    m.macro_regiao,
    m.micro_regiao,

    -- 4. População (Join pelo Ano e IBGE de 6 dígitos)
    pop.populacao_total,
    pop.populacao_6_12

FROM teste.producao_raw p
LEFT JOIN teste.municipios_ms m 
    ON p.municipio = m.codigo_ibge
LEFT JOIN teste.populacao_raw pop 
    ON pop.ano = EXTRACT(YEAR FROM p.data) 
    AND FLOOR(pop.municipio / 10) = p.municipio;