# Retomada - banco e views do app

Registro criado em 2026-05-16 para continuar o projeto em outro chat/desktop.

## Leitura rapida

O ano de 2023 ja esta extraido, revisado ate `fisioterapia` com olho humano e carregado no banco local `enade_postgres`.

Foram criadas views SQL para o aplicativo consumir apenas as questoes finais corretas de cada prova.

Arquivos mais importantes:

- `docs/PROXIMO_CHAT.md`: guia curto de retomada.
- `docs/CONTINUIDADE_EXTRACAO.md`: historico maior da extracao.
- `scripts/parser/escopo_manual_2023.py`: lista humana de questoes fora do escopo ate `fisioterapia`.
- `banco.sql/script_banco.sql`: schema atual do banco.
- `scripts/banco/carregar_staging.py`: carrega JSONs para `QUESTAO_STAGING`.
- `scripts/banco/popular_final.sql`: popula a camada final.
- `banco.sql/views/`: views do app.
- `banco.sql/views/MAPA_PROVAS_2023.md`: mapa `prova_id` x prova/curso.
- `banco.sql/views/criar_todas_views_2023.sql`: cria todas as views de 2023.

## Objetivo do projeto

Montar uma base PostgreSQL de questoes objetivas textuais do ENADE.

Entram na camada final apenas questoes que podem ser respondidas sem depender de imagem, grafico, tabela, mapa, figura, planta, foto, diagrama, radiografia ou estrutura visual do PDF.

Em caso de duvida, a regra do projeto e marcar como `fora_escopo`.

## Estado da extracao 2023

Resumo atual:

```text
28 cursos processados
1064 questoes no staging
655 questoes completas
409 questoes fora do escopo
0 questoes incompletas
0 cursos pendentes
```

Auditoria automatica final:

```text
PROBLEMAS FORTES
Nenhum problema forte encontrado nas questoes completas.

INCONSISTENCIAS COM DETECTOR/REVISAO HUMANA
Nenhuma inconsistencia encontrada.
```

Comando usado:

```powershell
python scripts/parser/auditar_qualidade.py --falhar-se-problema
```

## Revisao humana aplicada

O usuario revisou visualmente, PDF por PDF, os cursos de `engenharia_civil` ate `fisioterapia`.

A lista humana de questoes que NAO devem ir para o escopo ficou registrada em:

```text
scripts/parser/escopo_manual_2023.py
```

Essa lista e aplicada em tres pontos:

- `scripts/parser/processar_prova_v2.py`: marca como `fora_escopo` no processamento.
- `scripts/parser/auditar_qualidade.py`: falha se alguma questao manual voltar para `completa`.
- `scripts/banco/carregar_staging.py`: garante `FORA_ESCOPO` na carga do banco.

Cursos depois de `fisioterapia` ainda podem receber olho humano amostral antes de considerar 2023 definitivo.

## Banco local

Banco usado:

```text
enade_postgres
schema: public
usuario local usado: postgres
```

Nao registrar senha em docs nem commits. Use as credenciais locais ja configuradas no desktop.

Schema atual:

- `ANO`
- `CURSO`
- `PROVA`
- `QUESTAO_STAGING`
- `QUESTAO`
- `ALTERNATIVA`
- `GABARITO`

Mudancas importantes feitas em 2026-05-16:

- `criado_em` foi removido de `PROVA`, `QUESTAO_STAGING` e `QUESTAO`.
- `CURSO` ganhou a coluna `SLUG`.
- nomes dos cursos foram normalizados para exibicao com acentos e capitalizacao correta no banco.
- `popular_final.sql` agora so leva questoes com `STATUS = 'COMPLETA'`, `ALTERNATIVAS_COMPLETAS = TRUE`, `GABARITO_RESPOSTA IS NOT NULL` e `VERSAO_PARSER = 'V2'`.
- `popular_final.sql` tambem remove da camada final questoes que deixaram de ser elegiveis depois de nova revisao/parser.

## Contagens atuais no banco

Validacao final em 2026-05-16:

```text
questao_staging: 1064
questao: 651
gabarito: 651
alternativa: 3230
```

Status no staging:

```text
COMPLETA: 655
FORA_ESCOPO: 409
```

Integridade da camada final:

```text
colunas criado_em restantes: 0
questoes finais sem gabarito: 0
questoes finais sem staging elegivel: 0
problemas de OCR nos campos finais: 0
```

Observacao: existem 655 questoes `COMPLETA` no staging, mas 651 entram na camada final porque 4 questoes completas nao possuem gabarito/resposta oficial e foram corretamente excluidas.

Questoes completas sem gabarito final:

- Engenharia de Alimentos Q12
- Engenharia Eletrica Q30
- Engenharia Florestal Q28
- Odontologia Q26

## Limpeza de texto

Arquivo principal:

```text
scripts/parser/pos_processar_exibicao.py
```

Foram corrigidos problemas recorrentes de OCR nos campos exibidos:

- `insufi cientes` -> `insuficientes`
- `legislati vas` -> `legislativas`
- `politi ca` -> `politica`

Validacao: os campos finais do banco ficaram com 0 ocorrencias dos problemas buscados.

Obs.: `texto_bruto` pode continuar contendo problemas do PDF original, pois ele serve para auditoria/depuracao. O app deve consumir a camada final ou as views.

## Views do app

Pasta criada:

```text
banco.sql/views/
```

Arquivos:

- `banco.sql/views/README.md`
- `banco.sql/views/00_views_base_app.sql`
- `banco.sql/views/01_mapa_provas_2023.sql`
- `banco.sql/views/MAPA_PROVAS_2023.md`
- `banco.sql/views/criar_todas_views_2023.sql`
- `banco.sql/views/provas_2023/*.sql`

Views base:

- `vw_app_mapa_provas`
- `vw_app_questoes`

Views individuais por prova:

```text
vw_app_2023_agronomia
vw_app_2023_arquitetura_e_urbanismo
vw_app_2023_biomedicina
...
vw_app_2023_zootecnia
```

Total:

```text
28 views individuais
651 questoes somadas nas views
0 problemas de contagem
```

Cada view individual retorna:

- `prova_id`
- `ano`
- `curso_id`
- `curso_slug`
- `curso`
- `prova_titulo`
- `questao_id`
- `numero_questao`
- `enunciado`
- `alternativa_a`
- `alternativa_b`
- `alternativa_c`
- `alternativa_d`
- `alternativa_e`
- `alternativas` em JSONB
- `total_alternativas`
- `gabarito`

Exemplo para o app:

```sql
SELECT *
FROM vw_app_2023_agronomia
ORDER BY numero_questao;
```

## Mapa atual de prova_id

O mapa completo esta em:

```text
banco.sql/views/MAPA_PROVAS_2023.md
```

Resumo:

| prova_id | curso_slug | questoes finais |
|---:|---|---:|
| 1 | agronomia | 29 |
| 2 | arquitetura_e_urbanismo | 15 |
| 3 | biomedicina | 20 |
| 4 | enfermagem | 28 |
| 5 | engenharia_ambiental | 24 |
| 6 | engenharia_civil | 18 |
| 7 | engenharia_da_computacao | 20 |
| 8 | engenharia_de_alimentos | 21 |
| 9 | engenharia_de_controle_e_automacao | 13 |
| 10 | engenharia_de_producao | 12 |
| 11 | engenharia_eletrica | 10 |
| 12 | engenharia_florestal | 22 |
| 13 | engenharia_mecanica | 17 |
| 14 | engenharia_quimica | 9 |
| 15 | farmacia | 24 |
| 16 | fisioterapia | 26 |
| 17 | fonoaudiologia | 28 |
| 18 | medicina | 30 |
| 19 | medicina_veterinaria | 28 |
| 20 | nutricao | 31 |
| 21 | odontologia | 28 |
| 22 | tecnologia_em_agronegocio | 29 |
| 23 | tecnologia_em_estetica_e_cosmetico | 27 |
| 24 | tecnologia_em_gestao_ambiental | 26 |
| 25 | tecnologia_em_gestao_hospitalar | 31 |
| 26 | tecnologia_em_radiologia | 22 |
| 27 | tecnologia_em_seguranca_do_trabalho | 31 |
| 28 | zootecnia | 32 |

Importante: esses IDs correspondem ao banco local atual. Se o banco for recriado do zero em outro ambiente, confira novamente com:

```sql
SELECT *
FROM vw_app_mapa_provas
WHERE ano = 2023
ORDER BY curso_slug;
```

## Comandos importantes

Criar/ajustar schema:

```powershell
psql -h localhost -p 5432 -U postgres -d enade_postgres -f banco.sql/script_banco.sql
```

Reprocessar todos os cursos de 2023:

```powershell
python scripts/parser/processar_lote_2023.py
```

Auditar JSONs:

```powershell
python scripts/parser/auditar_qualidade.py --falhar-se-problema
```

Carregar staging:

```powershell
python scripts/banco/carregar_staging.py --host localhost --port 5432 --dbname enade_postgres --user postgres --password SUA_SENHA
```

Popular camada final:

```powershell
psql -h localhost -p 5432 -U postgres -d enade_postgres -f scripts/banco/popular_final.sql
```

Criar todas as views do app:

```powershell
psql -h localhost -p 5432 -U postgres -d enade_postgres -f banco.sql/views/criar_todas_views_2023.sql
```

Consultar mapa de provas:

```sql
SELECT prova_id, ano, curso_slug, curso, total_questoes
FROM vw_app_mapa_provas
WHERE ano = 2023
ORDER BY curso_slug;
```

Consultar uma prova no app:

```sql
SELECT *
FROM vw_app_2023_agronomia
ORDER BY numero_questao;
```

## Consultas de validacao

Contagens gerais:

```sql
SELECT 'questao_staging' AS tabela, COUNT(*) AS total FROM questao_staging
UNION ALL SELECT 'questao', COUNT(*) FROM questao
UNION ALL SELECT 'gabarito', COUNT(*) FROM gabarito
UNION ALL SELECT 'alternativa', COUNT(*) FROM alternativa;
```

Status do staging:

```sql
SELECT status, COUNT(*) AS total
FROM questao_staging
GROUP BY status
ORDER BY status;
```

Questao final sem gabarito:

```sql
SELECT COUNT(*) AS finais_sem_gabarito
FROM questao q
LEFT JOIN gabarito g ON g.questao_id = q.id
WHERE g.id IS NULL;
```

Validar views:

```sql
SELECT COUNT(*) AS provas_mapeadas
FROM vw_app_mapa_provas
WHERE ano = 2023;

SELECT COUNT(*) AS questoes_base
FROM vw_app_questoes
WHERE ano = 2023;
```

## Proximo passo recomendado

1. Confirmar se o app vai consumir uma view por prova (`vw_app_2023_agronomia`) ou a view base filtrando por `prova_id`.
2. Revisar uma amostra humana dos cursos apos `fisioterapia`, se quiser fechar 2023 com mais seguranca.
3. Depois, iniciar o mesmo fluxo para anos anteriores, provavelmente 2022 ou 2021.
4. Antes de subir para o GitHub, revisar `git status` e conferir se os arquivos `output/v2` gerados devem mesmo ir para o repositorio.

## Observacoes para o proximo chat

- Nao apagar nem reverter alteracoes locais sem pedir ao usuario.
- A senha do PostgreSQL foi informada no chat anterior, mas nao deve ser registrada em arquivo.
- O banco local ja possui as views criadas.
- Os arquivos SQL das views estao versionaveis em `banco.sql/views/`.
- Se algum curso for revisado novamente, reprocessar, auditar, recarregar staging, popular final e recriar views se necessario.
