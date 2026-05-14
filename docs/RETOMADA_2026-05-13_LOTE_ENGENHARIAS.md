# Retomada - lote de engenharias 2023

Registro criado em 2026-05-13 para continuar o projeto em outro desktop.

## Estado atual

O ano de 2023 esta com 17 cursos processados em `output/v2` e 11 cursos pendentes.

Auditoria geral atual:

```text
405 completa
241 fora_escopo
0 incompleta
```

Comando usado para validar:

```powershell
.\.venv\Scripts\python.exe scripts/parser/auditar_qualidade.py --falhar-se-problema
```

## Cursos processados nesta etapa

Foram baixados os PDFs oficiais e processados estes 5 cursos:

- `engenharia_civil`
- `engenharia_de_alimentos`
- `engenharia_da_computacao`
- `engenharia_de_controle_e_automacao`
- `engenharia_de_producao`

Resumo do lote:

| Curso | Completas | Fora de escopo | Incompletas |
|---|---:|---:|---:|
| Engenharia Civil | 18 | 20 | 0 |
| Engenharia de Alimentos | 23 | 15 | 0 |
| Engenharia da Computacao | 23 | 15 | 0 |
| Engenharia de Controle e Automacao | 14 | 24 | 0 |
| Engenharia de Producao | 13 | 25 | 0 |

## Conferencia humana feita

Engenharia Civil foi revisada manualmente pelo usuario e apontou problemas nas Q17 e Q36.

Decisao atual:

- `Engenharia Civil Q17`: `fora_escopo`, porque depende de formula matematica visual e a extracao perde a estrutura correta.
- `Engenharia Civil Q36`: `fora_escopo`, porque depende de pseudocodigo estruturado.

Lista final das questoes no escopo de Engenharia Civil:

```text
2, 4, 7, 8, 9, 10, 11, 13, 14, 15, 16, 23, 24, 26, 27, 31, 32, 34
```

## Correcoes feitas no parser

Arquivos principais alterados:

- `scripts/parser/processar_prova_v2.py`
- `scripts/parser/pos_processar_exibicao.py`
- `scripts/parser/auditar_qualidade.py`
- `scripts/parser/ver_questoes.py`
- `scripts/parser/processar_lote_2023.py`

Mudancas relevantes:

- O parser aceita alternativas `A-D` e `A-E`, gravando `alternativas_esperadas`.
- A auditoria e o visualizador respeitam `alternativas_esperadas`.
- Medicina 2023 foi corrigida: 30 `completa`, 8 `fora_escopo`, 0 `incompleta`.
- Engenharia Civil Q17/Q36 agora saem do escopo.
- Engenharia de Controle e Automacao Q22 sai do escopo por circuito/equacao booleana visual.
- Rodapes de cursos com nome composto passaram a ser removidos das alternativas, por exemplo `18 Engenharia Civil` e `34 Engenharia de Alimentos`.
- Tabelas clinicas extraidas como texto foram reforcadas como `fora_escopo`.

## Comandos uteis

Auditoria geral:

```powershell
.\.venv\Scripts\python.exe scripts/parser/auditar_qualidade.py --falhar-se-problema
```

Listar cursos ja no lote atual:

```powershell
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py --listar
```

Listar cursos pendentes:

```powershell
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py --pendentes --listar
```

Ver questoes no escopo de Engenharia Civil:

```powershell
.\.venv\Scripts\python.exe scripts/parser/ver_questoes.py output/v2/2023_engenharia_civil/2023_pv_engenharia_civil_questoes.json --status completa --limite 0
```

Salvar questoes no escopo de Engenharia Civil em TXT:

```powershell
.\.venv\Scripts\python.exe scripts/parser/ver_questoes.py output/v2/2023_engenharia_civil/2023_pv_engenharia_civil_questoes.json --status completa --limite 0 > engenharia_civil_completas.txt
```

## Cursos pendentes de 2023

- `engenharia_eletrica`
- `engenharia_florestal`
- `engenharia_mecanica`
- `engenharia_quimica`
- `zootecnia`
- `tecnologia_em_agronegocio`
- `tecnologia_em_estetica_e_cosmetico`
- `tecnologia_em_gestao_ambiental`
- `tecnologia_em_gestao_hospitalar`
- `tecnologia_em_radiologia`
- `tecnologia_em_seguranca_do_trabalho`

## Observacao para outro desktop

Se o ambiente Python ainda nao existir no outro desktop:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Depois rode a auditoria geral antes de continuar.
