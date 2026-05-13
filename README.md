# ENADE Postgres

Projeto para coletar PDFs oficiais do ENADE, extrair questoes objetivas, limpar o texto e carregar os dados em PostgreSQL.

## Fluxo principal

1. Baixar ou manter os PDFs em `pdfs/`.
2. Processar prova e gabarito com `scripts/parser/processar_prova_v2.py`.
3. Conferir as saidas em `output/v2/<ano_curso>/`.
4. Carregar os JSONs para staging com `scripts/banco/carregar_staging.py`.
5. Popular a camada final com `scripts/banco/popular_final.sql`.

## Pastas

- `pdfs/`: PDFs de prova (`PV`) e gabarito (`GB`).
- `scripts/coleta/`: scripts de coleta, filtro e validacao dos PDFs.
- `scripts/parser/`: extracao, classificacao, limpeza e verificacao das questoes.
- `scripts/banco/`: carga para o banco e popularizacao da camada final.
- `output/v2/`: saidas atuais do parser por ano e curso.
- `output/v1/`: saidas antigas mantidas como historico.
- `output/csv/`: CSVs auxiliares gerados na etapa de coleta.
- `banco.sql/`: scripts SQL de criacao e consulta do banco.

## Observacoes

O fluxo atual usa a versao `v2` do parser. Arquivos com sufixo `nv` ou `v2_new` parecem versoes experimentais/alternativas e devem ser revisados antes de serem removidos.

## Continuidade do trabalho

Antes de continuar em outro chat, leia:

- `docs/PROXIMO_CHAT.md`
- `docs/CONTINUIDADE_EXTRACAO.md`

O primeiro e um guia rapido de retomada. O segundo registra as regras de escopo, cursos ja processados, pendencias conhecidas, comandos de revisao/processamento e o estado atual da auditoria de qualidade.

Comandos uteis:

```powershell
python scripts/parser/auditar_qualidade.py --falhar-se-problema
python scripts/parser/processar_lote_2023.py --listar
```
