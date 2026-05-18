-- ============================================
-- VIEW APP - ENADE 2023 - Tecnologia em Radiologia
-- ============================================
-- Prova ID atual: 26
-- Curso ID atual: 26
-- Quest?es finais esperadas: 22
-- Esta view depende de banco.sql/views/00_views_base_app.sql.

CREATE OR REPLACE VIEW vw_app_2023_tecnologia_em_radiologia AS
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
WHERE PROVA_ID = 26;

COMMENT ON VIEW vw_app_2023_tecnologia_em_radiologia IS
'Quest?es finais para o app: ENADE 2023 - Tecnologia em Radiologia. Prova ID atual: 26.';
