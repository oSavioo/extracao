-- ============================================
-- VIEW APP - ENADE 2023 - Engenharia de Alimentos
-- ============================================
-- Prova ID atual: 8
-- Curso ID atual: 8
-- Quest?es finais esperadas: 21
-- Esta view depende de banco.sql/views/00_views_base_app.sql.

CREATE OR REPLACE VIEW vw_app_2023_engenharia_de_alimentos AS
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
WHERE PROVA_ID = 8;

COMMENT ON VIEW vw_app_2023_engenharia_de_alimentos IS
'Quest?es finais para o app: ENADE 2023 - Engenharia de Alimentos. Prova ID atual: 8.';
