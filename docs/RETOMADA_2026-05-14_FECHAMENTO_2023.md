# Retomada - fechamento 2023

Registro criado em 2026-05-14 para continuar o projeto em outro desktop.

## Estado atual

O ano de 2023 esta totalmente extraido em `output/v2`.

Resumo da auditoria final:

```text
28 cursos processados
668 completa
396 fora_escopo
0 incompleta
0 cursos pendentes
```

Comando usado para validar:

```powershell
.\.venv\Scripts\python.exe scripts/parser/auditar_qualidade.py --falhar-se-problema
```

## Marco de conferencia humana

A ultima conferencia com olho humano feita pelo usuario foi em `engenharia_civil`.

Decisoes confirmadas em Engenharia Civil:

- Q17 ficou `fora_escopo`, pois depende de formula matematica visual e a estrutura nao fica confiavel na extracao textual.
- Q36 ficou `fora_escopo`, pois depende de pseudocodigo estruturado.

Depois de Engenharia Civil, os demais cursos de 2023 foram refinados por auditoria automatica e regras conservadoras de descarte visual. Em 2026-05-14 foi feita uma revisao em modo estudante: as questoes completas foram triadas como se fossem resolvidas, e casos com dependencia visual/layout ruim foram movidos para `fora_escopo`. Ainda e recomendado um olho humano amostral antes de carga definitiva no banco final.

## Cursos extraidos em 2023

| Curso | Completas | Fora de escopo | Incompletas |
|---|---:|---:|---:|
| agronomia | 29 | 9 | 0 |
| arquitetura_e_urbanismo | 15 | 23 | 0 |
| biomedicina | 20 | 18 | 0 |
| enfermagem | 28 | 10 | 0 |
| engenharia_ambiental | 24 | 14 | 0 |
| engenharia_civil | 18 | 20 | 0 |
| engenharia_da_computacao | 22 | 16 | 0 |
| engenharia_de_alimentos | 23 | 15 | 0 |
| engenharia_de_controle_e_automacao | 14 | 24 | 0 |
| engenharia_de_producao | 12 | 26 | 0 |
| engenharia_eletrica | 15 | 23 | 0 |
| engenharia_florestal | 24 | 14 | 0 |
| engenharia_mecanica | 18 | 20 | 0 |
| engenharia_quimica | 10 | 28 | 0 |
| farmacia | 26 | 12 | 0 |
| fisioterapia | 26 | 12 | 0 |
| fonoaudiologia | 28 | 10 | 0 |
| medicina | 30 | 8 | 0 |
| medicina_veterinaria | 28 | 10 | 0 |
| nutricao | 31 | 7 | 0 |
| odontologia | 29 | 9 | 0 |
| tecnologia_em_agronegocio | 29 | 9 | 0 |
| tecnologia_em_estetica_e_cosmetico | 27 | 11 | 0 |
| tecnologia_em_gestao_ambiental | 26 | 12 | 0 |
| tecnologia_em_gestao_hospitalar | 31 | 7 | 0 |
| tecnologia_em_radiologia | 22 | 16 | 0 |
| tecnologia_em_seguranca_do_trabalho | 31 | 7 | 0 |
| zootecnia | 32 | 6 | 0 |

Total: 1064 questoes de prova, sendo 668 no escopo textual e 396 fora de escopo.

## Cursos extraidos nesta virada

Foram baixados os PDFs oficiais e processados os 11 cursos que faltavam:

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

## Refinamentos aplicados

Arquivo principal alterado: `scripts/parser/pos_processar_exibicao.py`.

Foram reforcadas regras para mandar a `fora_escopo` questoes que dependem de:

- grafico de nivel de tanque por tempo;
- modelo de reator com conservacao de massa e lei de Fick;
- infografico;
- mapas;
- esquemas e figuras citadas no enunciado;
- fluxogramas;
- folha ou outro elemento representado visualmente;
- figura indicada por referencia textual;
- pseudocodigo estruturado e formulas visuais ja identificados em Engenharia Civil.
- notacao matematica/formula que ficou quebrada e nao permite resolucao segura apenas por texto.

Na revisao em modo estudante tambem foram movidas para `fora_escopo`:

- `engenharia_da_computacao` Q18, por notacao matematica/O-grande quebrada nas alternativas;
- `engenharia_de_producao` Q38, por depender de esquema de ambientes;
- `engenharia_florestal` Q29, por depender de folha representada visualmente;
- `engenharia_quimica` Q16, por depender de fluxograma;
- `engenharia_quimica` Q25, por equacoes/layout matematico quebrado.

Foram removidos rodapes soltos de alternativas, como nomes de curso com numero de pagina, e restos de `Disponivel em:`/`Acesso em:` que sobravam no texto exibido.

Tambem foi atualizado `scripts/parser/processar_lote_2023.py`:

- `CURSOS_ATUAIS_2023` agora contem os 28 cursos de 2023;
- `CURSOS_PENDENTES_2023` esta vazio.

## Auditorias extras realizadas

Foram feitas varreduras nas questoes `completa` para procurar:

- rodape `VALIDINEP`;
- sobras de cabecalho/rodape em campos principais;
- frases fortes de dependencia visual;
- questoes `incompleta`.

Resultado: nenhum problema encontrado nas varreduras finais.

Varreduras finais adicionais:

```text
ARTEFATOS_EM_COMPLETAS 0
CARACTERES_INVALIDOS_EM_COMPLETAS 0
VISUAL_FORTE_NAO_JUSTIFICADO 0
TRAILING_FOOTER_CANDIDATES 0
```

## Comandos uteis

Auditoria geral:

```powershell
.\.venv\Scripts\python.exe scripts/parser/auditar_qualidade.py --falhar-se-problema
```

Listar todos os cursos de 2023:

```powershell
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py --listar
```

Confirmar pendentes:

```powershell
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py --pendentes --listar
```

Ver questoes completas de um curso:

```powershell
.\.venv\Scripts\python.exe scripts/parser/ver_questoes.py output/v2/2023_engenharia_eletrica/2023_pv_engenharia_eletrica_questoes.json --status completa --limite 0
```

Salvar questoes completas para revisao humana:

```powershell
.\.venv\Scripts\python.exe scripts/parser/ver_questoes.py output/v2/2023_engenharia_eletrica/2023_pv_engenharia_eletrica_questoes.json --status completa --limite 0 > engenharia_eletrica_completas.txt
```

## Planilha de conferencia

Foi gerada a planilha:

```text
output/revisoes/questoes_escopo_2023_engenharia_civil_em_diante.xlsx
```

Ela lista todas as questoes no escopo dos cursos de `engenharia_civil` em diante, seguindo a ordem de `scripts/parser/processar_lote_2023.py`.

Conteudo:

- aba `Resumo por curso`: `Curso`, `Questoes no escopo`, `Link da prova`, `Total no escopo`;
- aba `Questao por linha`: `Curso`, `Questao`, `Link da prova`;
- total da planilha: 23 cursos e 552 questoes `completa`.

## Proximo passo recomendado

Fazer olho humano dos cursos que vieram depois de Engenharia Civil, com prioridade para os cursos com mais descarte visual:

- `engenharia_quimica`
- `engenharia_de_producao`
- `engenharia_de_controle_e_automacao`
- `engenharia_eletrica`
- `arquitetura_e_urbanismo`
- `engenharia_mecanica`

Depois da revisao humana, carregar staging e popular a camada final somente com `completa`.
