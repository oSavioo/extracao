-- ============================================
-- CRIAR TODAS AS VIEWS DO APP - 2023
-- ============================================
-- Rode a partir da raiz do projeto:
-- psql -d enade_postgres -f banco.sql/views/criar_todas_views_2023.sql

\i banco.sql/views/00_views_base_app.sql
\i banco.sql/views/provas_2023/vw_app_2023_agronomia.sql
\i banco.sql/views/provas_2023/vw_app_2023_arquitetura_e_urbanismo.sql
\i banco.sql/views/provas_2023/vw_app_2023_biomedicina.sql
\i banco.sql/views/provas_2023/vw_app_2023_enfermagem.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_ambiental.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_civil.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_da_computacao.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_de_alimentos.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_de_controle_e_automacao.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_de_producao.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_eletrica.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_florestal.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_mecanica.sql
\i banco.sql/views/provas_2023/vw_app_2023_engenharia_quimica.sql
\i banco.sql/views/provas_2023/vw_app_2023_farmacia.sql
\i banco.sql/views/provas_2023/vw_app_2023_fisioterapia.sql
\i banco.sql/views/provas_2023/vw_app_2023_fonoaudiologia.sql
\i banco.sql/views/provas_2023/vw_app_2023_medicina.sql
\i banco.sql/views/provas_2023/vw_app_2023_medicina_veterinaria.sql
\i banco.sql/views/provas_2023/vw_app_2023_nutricao.sql
\i banco.sql/views/provas_2023/vw_app_2023_odontologia.sql
\i banco.sql/views/provas_2023/vw_app_2023_tecnologia_em_agronegocio.sql
\i banco.sql/views/provas_2023/vw_app_2023_tecnologia_em_estetica_e_cosmetico.sql
\i banco.sql/views/provas_2023/vw_app_2023_tecnologia_em_gestao_ambiental.sql
\i banco.sql/views/provas_2023/vw_app_2023_tecnologia_em_gestao_hospitalar.sql
\i banco.sql/views/provas_2023/vw_app_2023_tecnologia_em_radiologia.sql
\i banco.sql/views/provas_2023/vw_app_2023_tecnologia_em_seguranca_do_trabalho.sql
\i banco.sql/views/provas_2023/vw_app_2023_zootecnia.sql

-- Validacao rapida
SELECT PROVA_ID, ANO, CURSO_SLUG, CURSO, TOTAL_QUESTOES
FROM vw_app_mapa_provas
WHERE ANO = 2023
ORDER BY CURSO_SLUG;
