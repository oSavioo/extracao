-- ============================================
-- VIEW APP - ENADE 2023 - Tecnologia em Gestão Ambiental
-- ============================================
-- Prova ID atual: 24
-- Curso ID atual: 24
-- Quest?es finais esperadas: 26
-- Esta view depende de banco.sql/views/00_views_base_app.sql.

CREATE OR REPLACE VIEW vw_app_2023_tecnologia_em_gestao_ambiental AS
SELECT
    PROVA_ID,
    ANO,
    CURSO_ID,
    CURSO_SLUG,
    CURSO,
    PROVA_TITULO,
    QUESTAO_ID,
    NUMERO_QUESTAO,
    ENUNCIADO,
    ALTERNATIVA_A,
    ALTERNATIVA_B,
    ALTERNATIVA_C,
    ALTERNATIVA_D,
    ALTERNATIVA_E,
    ALTERNATIVAS,
    TOTAL_ALTERNATIVAS,
    GABARITO
FROM vw_app_questoes
WHERE PROVA_ID = 24;

COMMENT ON VIEW vw_app_2023_tecnologia_em_gestao_ambiental IS
'Quest?es finais para o app: ENADE 2023 - Tecnologia em Gestão Ambiental. Prova ID atual: 24.';
