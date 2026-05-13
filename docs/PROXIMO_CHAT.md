# Proximo chat - guia rapido

Este arquivo e o ponto de entrada rapido para continuar a extracao.
Para detalhes completos, leia tambem `docs/CONTINUIDADE_EXTRACAO.md`.

## Objetivo atual

Extrair questoes objetivas textuais do ENADE para PostgreSQL.

Entra no banco final apenas questao `completa` que possa ser respondida sem imagem, grafico, tabela, quadro, mapa, planta, foto, diagrama ou qualquer elemento visual.

Em caso de duvida, marque como `fora_escopo`.

## Estado atual

Cursos 2023 ja processados em `output/v2`:

- agronomia
- arquitetura_e_urbanismo
- biomedicina
- enfermagem
- engenharia_ambiental
- farmacia
- fisioterapia
- fonoaudiologia
- medicina
- medicina_veterinaria
- nutricao
- odontologia

Atencao: `medicina` ainda nao esta pronta. Muitas questoes ficaram `incompleta`, entao nao use Medicina para carga final ate corrigir o parser desse curso.

## Primeiro comando recomendado

Rode a auditoria automatica:

```powershell
python scripts/parser/auditar_qualidade.py --falhar-se-problema
```

Auditar um curso especifico:

```powershell
python scripts/parser/auditar_qualidade.py --curso agronomia --falhar-se-problema
```

## Ver questoes para revisao humana

Questoes completas de um curso:

```powershell
python scripts/parser/ver_questoes.py output/v2/2023_agronomia/2023_pv_agronomia_questoes.json --status completa --limite 0
```

Questoes fora do escopo:

```powershell
python scripts/parser/ver_questoes.py output/v2/2023_agronomia/2023_pv_agronomia_questoes.json --status fora_escopo --limite 0
```

Intervalo especifico:

```powershell
python scripts/parser/ver_questoes.py output/v2/2023_agronomia/2023_pv_agronomia_questoes.json --status completa --inicio 10 --fim 20 --limite 0
```

Salvar em TXT para comparar com o PDF:

```powershell
python scripts/parser/ver_questoes.py output/v2/2023_agronomia/2023_pv_agronomia_questoes.json --status completa --limite 0 > agronomia_completas.txt
```

## Processar ou reprocessar

Um curso:

```powershell
python scripts/parser/processar_prova_v2.py --pv pdfs/2023_PV_agronomia.pdf --gb pdfs/2023_GB_agronomia.pdf --out-dir output/v2/2023_agronomia
```

Lote atual:

```powershell
python scripts/parser/processar_lote_2023.py
```

Curso especifico pelo lote:

```powershell
python scripts/parser/processar_lote_2023.py --curso biomedicina
```

Listar cursos e conferir se os PDFs existem:

```powershell
python scripts/parser/processar_lote_2023.py --listar
```

Listar cursos pendentes conhecidos:

```powershell
python scripts/parser/processar_lote_2023.py --pendentes --listar
```

## Proximos cursos 2023 pendentes

Estao em `output/csv/pdfs_objetivos_2023.csv` e tambem no script `scripts/parser/processar_lote_2023.py`:

- engenharia_civil
- engenharia_de_alimentos
- engenharia_da_computacao
- engenharia_de_controle_e_automacao
- engenharia_de_producao
- engenharia_eletrica
- engenharia_florestal
- engenharia_mecanica
- engenharia_quimica
- zootecnia
- tecnologia_em_agronegocio
- tecnologia_em_estetica_e_cosmetico
- tecnologia_em_gestao_ambiental
- tecnologia_em_gestao_hospitalar
- tecnologia_em_radiologia
- tecnologia_em_seguranca_do_trabalho

## Regras que deram problema antes

Marcar como `fora_escopo`:

- questao numero 6, sempre;
- questao com tabela extraida como texto;
- questao com foto, planta, fachada, mapa, vista, corte, imagem clinica ou micrografia;
- questao com termos como `observe`, `figura`, `imagem`, `tabela`, `grafico`, `quadro`, `mapa`, quando a resposta depender do elemento visual;
- questao em pagina com imagem incorporada e apenas uma questao objetiva identificavel;
- questao com series visuais como muitos percentuais, razoes ou comparadores.

Excecao importante: mencao textual a `imagem radiografica`, quando o resultado do exame ja esta descrito no enunciado e nao ha figura a analisar, pode continuar como `completa`.

## Fluxo seguro antes de carregar no banco

1. Baixar/processar o curso.
2. Revisar `completa` com `ver_questoes.py`.
3. Comparar com o PDF oficial.
4. Se uma questao visual passou, ajustar `scripts/parser/pos_processar_exibicao.py`.
5. Reprocessar o curso.
6. Rodar `auditar_qualidade.py --falhar-se-problema`.
7. So carregar no banco depois da revisao humana.
