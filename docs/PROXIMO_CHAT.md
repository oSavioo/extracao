# Proximo chat - guia rapido

Este arquivo e o ponto de entrada rapido para continuar a extracao.
Para detalhes completos, leia tambem `docs/CONTINUIDADE_EXTRACAO.md`.
Para o fechamento de 2023, leia `docs/RETOMADA_2026-05-14_FECHAMENTO_2023.md`.
Para o estado atual do banco e das views do app, leia `docs/RETOMADA_2026-05-16_BANCO_E_VIEWS.md`.

## Objetivo atual

Extrair questoes objetivas textuais do ENADE para PostgreSQL.

Entra no banco final apenas questao `completa` que possa ser respondida sem imagem, grafico, tabela, quadro, mapa, planta, foto, diagrama ou qualquer elemento visual.

Em caso de duvida, marque como `fora_escopo`.

## Estado atual

2023 esta totalmente extraido em `output/v2`.

Auditoria final:

```text
28 cursos processados
655 completa
409 fora_escopo
0 incompleta
0 cursos pendentes
```

A revisao com olho humano feita pelo usuario avancou ate `fisioterapia` inclusive, seguindo a ordem de `scripts/parser/processar_lote_2023.py`. Depois desse marco, os demais cursos de 2023 foram extraidos e refinados por auditoria automatica/regras conservadoras. Ainda e recomendado um olho humano amostral nos cursos apos `fisioterapia` antes de considerar 2023 definitivo.

Banco local `enade_postgres` carregado em 2026-05-16:

```text
questao_staging: 1064
questao: 651
gabarito: 651
alternativa: 3230
```

O schema atual nao usa mais coluna `criado_em` nas tabelas de prova/questao/staging. `curso` tem `slug`, e os nomes foram normalizados para exibicao com acentos.

Views do app criadas em `banco.sql/views/`:

```text
vw_app_mapa_provas
vw_app_questoes
vw_app_2023_<curso>
```

Validacao das views:

```text
28 views individuais
651 questoes somadas
0 problemas de contagem
```

## Onde paramos

- 2023 nao precisa ser extraido de novo, salvo se o parser mudar.
- Os PDFs e JSONs dos 28 cursos estao em `pdfs/` e `output/v2/`.
- `scripts/parser/processar_lote_2023.py` ja tem os 28 cursos em `CURSOS_ATUAIS_2023`.
- `CURSOS_PENDENTES_2023` esta vazio.
- As views do app ja foram criadas no banco local e tambem salvas como SQL em `banco.sql/views/`.
- O proximo trabalho natural e revisar uma amostra humana das `completa` dos cursos apos `fisioterapia` e depois seguir para anos anteriores.

Questoes movidas para `fora_escopo` na revisao em modo estudante:

- `engenharia_da_computacao` Q18;
- `engenharia_de_producao` Q38;
- `engenharia_florestal` Q29;
- `engenharia_quimica` Q16;
- `engenharia_quimica` Q25.

A lista manual de questoes fora do escopo revisadas ate `fisioterapia` esta registrada em `scripts/parser/escopo_manual_2023.py`.

## Planilha de conferencia

Foi gerada uma planilha Excel com as questoes `completa` dos cursos de `engenharia_civil` em diante:

```text
output/revisoes/questoes_escopo_2023_engenharia_civil_em_diante.xlsx
```

A planilha tem duas abas:

- `Resumo por curso`: curso, questoes no escopo, link da prova e total.
- `Questao por linha`: uma linha por questao, com curso, questao e link da prova.

Escopo da planilha: 23 cursos e 539 questoes `completa`.

## Primeiro comando recomendado

Se for apenas retomar contexto, leia primeiro:

```text
docs/RETOMADA_2026-05-16_BANCO_E_VIEWS.md
```

Depois rode a auditoria automatica:

```powershell
.\.venv\Scripts\python.exe scripts/parser/auditar_qualidade.py --falhar-se-problema
```

Auditar um curso especifico:

```powershell
.\.venv\Scripts\python.exe scripts/parser/auditar_qualidade.py --curso agronomia --falhar-se-problema
```

## Ver questoes para revisao humana

Questoes completas de um curso:

```powershell
.\.venv\Scripts\python.exe scripts/parser/ver_questoes.py output/v2/2023_agronomia/2023_pv_agronomia_questoes.json --status completa --limite 0
```

Questoes fora do escopo:

```powershell
.\.venv\Scripts\python.exe scripts/parser/ver_questoes.py output/v2/2023_agronomia/2023_pv_agronomia_questoes.json --status fora_escopo --limite 0
```

Intervalo especifico:

```powershell
.\.venv\Scripts\python.exe scripts/parser/ver_questoes.py output/v2/2023_agronomia/2023_pv_agronomia_questoes.json --status completa --inicio 10 --fim 20 --limite 0
```

Salvar em TXT para comparar com o PDF:

```powershell
.\.venv\Scripts\python.exe scripts/parser/ver_questoes.py output/v2/2023_agronomia/2023_pv_agronomia_questoes.json --status completa --limite 0 > agronomia_completas.txt
```

## Processar ou reprocessar

Um curso:

```powershell
.\.venv\Scripts\python.exe scripts/parser/processar_prova_v2.py --pv pdfs/2023_PV_agronomia.pdf --gb pdfs/2023_GB_agronomia.pdf --out-dir output/v2/2023_agronomia
```

Lote 2023 completo:

```powershell
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py
```

Curso especifico pelo lote:

```powershell
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py --curso biomedicina
```

Listar cursos e conferir se os PDFs existem:

```powershell
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py --listar
```

Confirmar pendentes:

```powershell
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py --pendentes --listar
```

## Pendentes 2023

Nao ha cursos pendentes no lote de 2023. `CURSOS_PENDENTES_2023` esta vazio em `scripts/parser/processar_lote_2023.py`.

## Views do app

Arquivos:

```text
banco.sql/views/README.md
banco.sql/views/MAPA_PROVAS_2023.md
banco.sql/views/00_views_base_app.sql
banco.sql/views/criar_todas_views_2023.sql
banco.sql/views/provas_2023/*.sql
```

Criar/recriar todas as views:

```powershell
psql -h localhost -p 5432 -U postgres -d enade_postgres -f banco.sql/views/criar_todas_views_2023.sql
```

Consultar uma prova no app:

```sql
SELECT *
FROM vw_app_2023_agronomia
ORDER BY numero_questao;
```

Consultar o mapa de provas:

```sql
SELECT prova_id, ano, curso_slug, curso, total_questoes
FROM vw_app_mapa_provas
WHERE ano = 2023
ORDER BY curso_slug;
```

## Regras que deram problema antes

Observacao de parser: prova/curso pode ter alternativas `A-D` ou `A-E`; conferir `alternativas_esperadas` antes de tratar `E` ausente como erro.

Marcar como `fora_escopo`:

- questao numero 6, sempre;
- questao com tabela extraida como texto;
- questao com foto, planta, fachada, mapa, vista, corte, imagem clinica ou micrografia;
- questao com termos como `observe`, `figura`, `imagem`, `tabela`, `grafico`, `quadro`, `mapa`, quando a resposta depender do elemento visual;
- questao em pagina com imagem incorporada e apenas uma questao objetiva identificavel;
- questao com series visuais como muitos percentuais, razoes ou comparadores;
- questao com formulas, pseudocodigo, infografico, esquema ou mapa cuja estrutura visual nao fique preservada no texto.

Excecao importante: mencao textual a `imagem radiografica`, quando o resultado do exame ja esta descrito no enunciado e nao ha figura a analisar, pode continuar como `completa`.

## Fluxo seguro antes de recarregar o banco

1. Rodar `auditar_qualidade.py --falhar-se-problema`.
2. Revisar uma amostra de `completa` com `ver_questoes.py`, comecando pelos cursos com mais descarte visual.
3. Comparar com o PDF oficial.
4. Se uma questao visual passou, ajustar `scripts/parser/pos_processar_exibicao.py`.
5. Reprocessar o curso.
6. Rodar novamente `auditar_qualidade.py --falhar-se-problema`.
7. Recarregar staging e rodar `scripts/banco/popular_final.sql`.
