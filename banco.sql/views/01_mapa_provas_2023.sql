-- ============================================
-- MAPA DAS PROVAS 2023
-- ============================================
-- Execute 00_views_base_app.sql antes deste arquivo.

SELECT
    PROVA_ID,
    ANO,
    CURSO_ID,
    CURSO_SLUG,
    CURSO,
    TOTAL_QUESTOES
FROM vw_app_mapa_provas
WHERE ANO = 2023
ORDER BY CURSO_SLUG;
