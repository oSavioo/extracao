-- ============================================
-- VIEW APP - ENADE 2023 - Arquitetura e Urbanismo
-- ============================================
-- Prova ID atual: 2
-- Curso ID atual: 2
-- Quest?es finais esperadas: 15
-- Esta view depende de banco.sql/views/00_views_base_app.sql.

CREATE OR REPLACE VIEW vw_app_2023_arquitetura_e_urbanismo AS
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
WHERE PROVA_ID = 2;

COMMENT ON VIEW vw_app_2023_arquitetura_e_urbanismo IS
'Quest?es finais para o app: ENADE 2023 - Arquitetura e Urbanismo. Prova ID atual: 2.';
