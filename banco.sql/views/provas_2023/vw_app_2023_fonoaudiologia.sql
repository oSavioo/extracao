-- ============================================
-- VIEW APP - ENADE 2023 - Fonoaudiologia
-- ============================================
-- Prova ID atual: 17
-- Curso ID atual: 17
-- Quest?es finais esperadas: 28
-- Esta view depende de banco.sql/views/00_views_base_app.sql.

CREATE OR REPLACE VIEW vw_app_2023_fonoaudiologia AS
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
WHERE PROVA_ID = 17;

COMMENT ON VIEW vw_app_2023_fonoaudiologia IS
'Quest?es finais para o app: ENADE 2023 - Fonoaudiologia. Prova ID atual: 17.';
