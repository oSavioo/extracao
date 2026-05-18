# Views do App

Esta pasta concentra as views SQL para o aplicativo consumir apenas as questoes finais do banco.

Arquivos principais:

- `00_views_base_app.sql`: cria `vw_app_mapa_provas` e `vw_app_questoes`.
- `MAPA_PROVAS_2023.md`: mostra qual `prova_id` corresponde a cada prova no banco local atual.
- `01_mapa_provas_2023.sql`: consulta SQL do mapa de provas.
- `provas_2023/`: uma view por prova, no padrao `vw_app_2023_<curso>`.
- `criar_todas_views_2023.sql`: executa a base e todas as views de 2023.

Para criar tudo no PostgreSQL, rode a partir da raiz do projeto:

```powershell
psql -d enade_postgres -f banco.sql/views/criar_todas_views_2023.sql
```

No app, consulte a view do curso desejado e ordene por `numero_questao`:

```sql
SELECT *
FROM vw_app_2023_agronomia
ORDER BY numero_questao;
```
