# Continuidade da Extração ENADE

Data deste registro: 2026-05-07.

Este documento resume o estado atual do trabalho para que outro chat consiga continuar sem depender do histórico da conversa.

Para o estado mais recente do banco e das views do app, leia tambem `docs/RETOMADA_2026-05-16_BANCO_E_VIEWS.md`.

## Objetivo do projeto

Construir uma base de questões objetivas do ENADE em PostgreSQL.

O foco atual é extrair apenas questões no modelo textual:

- enunciado completo em texto;
- alternativas completas conforme a prova (`A-D` ou `A-E`);
- gabarito associado;
- sem necessidade de analisar imagem, gráfico, tabela, mapa, figura, planta, foto, diagrama, radiografia ou qualquer elemento visual;
- texto adequado para exibição no jogo/banco, sem rodapé, URL solta, seção pós-prova ou artefato de PDF.

Questões fora desse modelo devem permanecer no JSON/staging para auditoria, mas não devem ir para a camada final jogável.

## Regra de escopo

### Entra como `completa`

Questão objetiva textual que pode ser respondida lendo apenas o enunciado e as alternativas.

Exemplos aceitos:

- caso clínico textual;
- texto-base + afirmações I/II/III;
- legislação/norma textual;
- interpretação textual sem imagem;
- questão de conhecimento técnico sem tabela ou figura.

### Entra como `fora_escopo`

Qualquer questão que dependa ou pareça depender de:

- gráfico, tabela, quadro, mapa, figura, imagem, foto, charge, cartum, ícone ou infográfico;
- planta, fachada, vista, corte, implantação, elevação ou desenho técnico;
- radiografia, tomografia, ultrassonografia, lâmina, micrografia ou imagem clínica;
- tabela extraída como texto, como exames laboratoriais/resultados/valores de referência;
- série visual extraída como texto, como muitos percentuais, razões ou comparadores;
- página do PDF que contém imagem incorporada e apenas uma questão objetiva identificável.

Preferência do projeto: em caso de dúvida, descartar para `fora_escopo`.

## Arquivos principais atuais

### Parser e pós-processamento

- `scripts/parser/processar_prova_v2.py`
  - Script principal de processamento.
  - Lê PDF de prova e gabarito.
  - Divide a prova por blocos `QUESTÃO X`.
  - Extrai alternativas em sequencias `A-D` ou `A-E`.
  - Chama `classificar_status_exibicao`.
  - Detecta páginas com imagens via `pypdf`.
  - Gera JSON, quarentena, relatório, debug e amostra.

- `scripts/parser/pos_processar_exibicao.py`
  - Limpeza de texto para exibição.
  - Regras de substituição de quebras de palavras.
  - Regras para classificar questões visuais como `fora_escopo`.
  - Remove seções pós-prova como `AVALIAÇÃO GLOBAL DA PROVA`.

- `scripts/parser/ver_questoes.py`
  - Ferramenta de revisão humana.
  - Permite filtrar por status, intervalo e limite.

### Banco

- `scripts/banco/carregar_staging.py`
  - Carrega os JSONs do `output/v2` para `QUESTAO_STAGING`.
  - Normaliza status para maiúsculas.

- `scripts/banco/popular_final.sql`
  - Popula a camada final.
  - Só insere questões com `STATUS = 'COMPLETA'` e `ALTERNATIVAS_COMPLETAS = TRUE`.

### Coleta

- `scripts/coleta/coletar_pdfs_2023.py`
- `scripts/coleta/filtrar_objetivas_2023.py`
- `scripts/coleta/validar_pares_2023.py`
- `scripts/coleta/baixar_prova_enade.py`

## Arquivos legados ou experimentais

Não remover sem nova revisão:

- `scripts/parser/processar_prova_nv.py`
- `scripts/parser/post_processar_exibicao_nv.py`
- `scripts/parser/processar_prova_v2_new.py`
- `output/v1/`

Esses arquivos não são o fluxo principal atual, mas podem servir como referência histórica.

## Cursos 2023 já processados

Resumo atual apos a revisao em modo estudante de 2026-05-14:

| Curso | Completas | Fora de escopo | Incompletas | Observação |
|---|---:|---:|---:|---|
| Agronomia | 29 | 9 | 0 | Q6 fora do escopo por regra do projeto |
| Arquitetura e Urbanismo | 15 | 23 | 0 | Q6 fora do escopo por regra do projeto |
| Biomedicina | 20 | 18 | 0 | Q6 fora do escopo por regra do projeto |
| Enfermagem | 28 | 10 | 0 | Q6 fora do escopo por regra do projeto |
| Engenharia Ambiental | 24 | 14 | 0 | Q6 fora do escopo por regra do projeto |
| Engenharia Civil | 18 | 20 | 0 | revisao humana aplicada ate Fisioterapia |
| Engenharia de Alimentos | 22 | 16 | 0 | revisao humana aplicada ate Fisioterapia |
| Engenharia da Computação | 20 | 18 | 0 | revisao humana aplicada ate Fisioterapia |
| Engenharia de Controle e Automação | 13 | 25 | 0 | revisao humana aplicada ate Fisioterapia |
| Engenharia de Produção | 12 | 26 | 0 | revisao humana aplicada ate Fisioterapia |
| Engenharia Elétrica | 11 | 27 | 0 | revisao humana aplicada ate Fisioterapia |
| Engenharia Florestal | 23 | 15 | 0 | revisao humana aplicada ate Fisioterapia |
| Engenharia Mecânica | 17 | 21 | 0 | revisao humana aplicada ate Fisioterapia |
| Engenharia Química | 9 | 29 | 0 | revisao humana aplicada ate Fisioterapia |
| Farmácia | 24 | 14 | 0 | revisao humana aplicada ate Fisioterapia |
| Fisioterapia | 26 | 12 | 0 | revisao humana aplicada ate Fisioterapia |
| Fonoaudiologia | 28 | 10 | 0 | Q6 fora do escopo por regra do projeto |
| Medicina | 30 | 8 | 0 | Parser ajustado para alternativas A-D; Q10 fora do escopo por tabela extraída como texto |
| Medicina Veterinária | 28 | 10 | 0 | Q6 fora do escopo por regra do projeto |
| Nutrição | 31 | 7 | 0 | Q6 fora do escopo por regra do projeto |
| Odontologia | 29 | 9 | 0 | Q23, Q25 e Q26 corrigidas como textuais; Q26 anulada no gabarito oficial |
| Tecnologia em Agronegócio | 29 | 9 | 0 | Q6 fora do escopo por regra do projeto |
| Tecnologia em Estética e Cosmético | 27 | 11 | 0 | Q6 fora do escopo por regra do projeto |
| Tecnologia em Gestão Ambiental | 26 | 12 | 0 | Q6 fora do escopo por regra do projeto |
| Tecnologia em Gestão Hospitalar | 31 | 7 | 0 | Q6 fora do escopo por regra do projeto |
| Tecnologia em Radiologia | 22 | 16 | 0 | Q6 fora do escopo por regra do projeto |
| Tecnologia em Segurança do Trabalho | 31 | 7 | 0 | Q6 fora do escopo por regra do projeto |
| Zootecnia | 32 | 6 | 0 | Q6 fora do escopo por regra do projeto |

Total atual de 2023: 28 cursos, 1064 questoes, 655 `completa`, 409 `fora_escopo` e 0 `incompleta`.

## Pendência crítica resolvida

### Medicina 2023

Medicina foi reprocessada em 2026-05-13 e não tem mais questões `incompleta`.

Correção aplicada:

- O componente específico da prova usa quatro alternativas (`A-D`), enquanto o parser antigo exigia `A-E`.
- `scripts/parser/processar_prova_v2.py` agora reconhece sequências `A-D` e `A-E`, preferindo `A-E` quando existir.
- O JSON passou a registrar `alternativas_esperadas`.
- `scripts/parser/auditar_qualidade.py` e `scripts/parser/ver_questoes.py` respeitam `alternativas_esperadas`.
- Q10 de Medicina foi marcada como `fora_escopo` por conter tabela clínica extraída como texto.

Resultado atual de Medicina: 30 `completa`, 8 `fora_escopo`, 0 `incompleta`.

## Comandos de revisão

Ver questões completas de um curso:

```powershell
python scripts/parser/ver_questoes.py output/v2/2023_nutricao/2023_pv_nutricao_questoes.json --status completa --limite 0
```

Ver questões fora do escopo:

```powershell
python scripts/parser/ver_questoes.py output/v2/2023_nutricao/2023_pv_nutricao_questoes.json --status fora_escopo --limite 0
```

Ver intervalo específico:

```powershell
python scripts/parser/ver_questoes.py output/v2/2023_nutricao/2023_pv_nutricao_questoes.json --status completa --inicio 20 --fim 30 --limite 0
```

Salvar revisão em arquivo:

```powershell
python scripts/parser/ver_questoes.py output/v2/2023_nutricao/2023_pv_nutricao_questoes.json --status completa --limite 0 > nutricao_completas.txt
```

## Comandos de processamento

Processar um curso:

```powershell
python scripts/parser/processar_prova_v2.py --pv pdfs/2023_PV_nutricao.pdf --gb pdfs/2023_GB_nutricao.pdf --out-dir output/v2/2023_nutricao
```

Processar lote atual de 2023:

```powershell
$cursos = @(
  'agronomia',
  'arquitetura_e_urbanismo',
  'biomedicina',
  'enfermagem',
  'engenharia_ambiental',
  'engenharia_civil',
  'engenharia_de_alimentos',
  'engenharia_da_computacao',
  'engenharia_de_controle_e_automacao',
  'engenharia_de_producao',
  'farmacia',
  'fisioterapia',
  'fonoaudiologia',
  'medicina',
  'medicina_veterinaria',
  'nutricao',
  'odontologia'
)

foreach ($curso in $cursos) {
  python scripts/parser/processar_prova_v2.py --pv "pdfs/2023_PV_$curso.pdf" --gb "pdfs/2023_GB_$curso.pdf" --out-dir "output/v2/2023_$curso"
}
```

## Baixar novos cursos de 2023

Exemplo:

```powershell
python scripts/coleta/baixar_prova_enade.py --ano 2023 --curso "zootecnia"
```

Ou manualmente seguindo o padrão:

```text
https://download.inep.gov.br/enade/provas_e_gabaritos/2023_PV_<curso>.pdf
https://download.inep.gov.br/enade/provas_e_gabaritos/2023_GB_<curso>.pdf
```

## Cursos disponíveis no CSV para adicionar depois

Já aparecem em `output/csv/pdfs_objetivos_2023.csv` e ainda podem ser processados:

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

## Auditoria automática usada na última revisão

Foi feita uma busca nas questões `completa` por padrões fortes de problema:

- `seguinte figura`;
- `figura 1`, `figura 2`, `figura 3`;
- rodapé `VALIDINEP`;
- seção `AVALIAÇÃO GLOBAL DA PROVA`;
- URLs soltas;
- caractere inválido `�`.

Resultado final:

```text
PROBLEMAS_FORTES 0
```

## Regras importantes adicionadas durante o trabalho

- Tabelas extraídas como texto devem ser `fora_escopo`.
- Questões com imagem por página são `fora_escopo` quando a página tem uma única questão objetiva identificável.
- Questões de Arquitetura com planta/fachada/vista/implantação/corte/foto/projeto visual devem ser descartadas.
- Questões com `seguinte figura` ou `Figura N` devem ser descartadas.
- Séries visuais de prevalência/razões, como `1:150`, `1:68`, `1:36`, devem ser descartadas.
- Não confiar apenas no fato de haver texto legível: se a resposta depende de elemento visual do PDF, é fora do escopo.

## Próximo passo recomendado

1. Nao ha extracao pendente para 2023.
2. O banco local `enade_postgres` ja foi carregado com os JSONs atuais.
3. Fazer olho humano amostral nos cursos apos `fisioterapia`, priorizando os restantes com maior descarte visual: `tecnologia_em_radiologia`, `tecnologia_em_gestao_ambiental`, `tecnologia_em_estetica_e_cosmetico`, `fonoaudiologia` e `medicina_veterinaria`.
4. Depois de estabilizar 2023, replicar o fluxo para anos anteriores, comecando por 2022 ou 2021 antes de ir ate 2015.

## Carga no banco

Quando a revisão humana aprovar os JSONs:

```powershell
python scripts/banco/carregar_staging.py --dbname SEU_BANCO --user SEU_USUARIO --password SUA_SENHA
```

Depois executar:

```sql
\i scripts/banco/popular_final.sql
```

## Ferramentas preparadas para retomada

Depois deste registro, foram adicionados dois utilitarios para reduzir trabalho manual no proximo chat:

- `scripts/parser/auditar_qualidade.py`
  - Audita os JSONs em `output/v2`.
  - Conta status por curso.
  - Procura problemas fortes em questoes `completa`.
  - Compara completas com o detector visual atual.
  - Aceita `--curso` para auditar curso especifico.

- `scripts/parser/processar_lote_2023.py`
  - Processa lote de cursos 2023 com o parser v2.
  - Aceita `--curso`, `--pendentes`, `--todos`, `--listar` e `--continuar-se-erro`.
  - Usa PDFs no padrao `pdfs/2023_PV_<curso>.pdf` e `pdfs/2023_GB_<curso>.pdf`.

Comandos recomendados para o proximo chat:

```powershell
.\.venv\Scripts\python.exe scripts/parser/auditar_qualidade.py --falhar-se-problema
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py --listar
.\.venv\Scripts\python.exe scripts/parser/processar_lote_2023.py --pendentes --listar
```

Tambem foi criado `docs/PROXIMO_CHAT.md`, que e o guia curto de retomada.

Lembrete: `popular_final.sql` só leva para a camada final o que está `COMPLETA`.

## Atualizacao de regra - 2026-05-12

- Questao 6 deve ser sempre `fora_escopo`, por regra do projeto.
- Mencao textual a `imagem radiografica` ou `imagens radiograficas`, quando o resultado do exame ja esta descrito no enunciado e nao ha figura a analisar, pode permanecer em `completa`.
- Odontologia 2023 foi reprocessada: Q23, Q25 e Q26 ficaram no escopo textual; Q26 esta anulada no gabarito oficial e nao deve ir para a camada final jogavel.
- Auditoria geral apos o reprocessamento: 289 `completa`, 141 `fora_escopo`, 26 `incompleta`.

## Atualizacao de regra - 2026-05-13

- Medicina 2023 foi corrigida e reprocessada: 30 `completa`, 8 `fora_escopo`, 0 `incompleta`.
- O parser v2 agora aceita provas com alternativas `A-D` ou `A-E`, gravando `alternativas_esperadas` para auditoria e visualizacao.
- `auditar_qualidade.py` e `ver_questoes.py` usam `alternativas_esperadas`, entao `E` ausente nao e problema quando a questao esperada e `A-D`.
- Q10 de Medicina 2023 deve ficar `fora_escopo`, pois contem tabela clinica extraida como texto (`Resultado Referencia`, citometria/citologia).
- Auditoria geral apos o reprocessamento: 314 `completa`, 142 `fora_escopo`, 0 `incompleta`.

## Atualizacao de lote - 2026-05-13

- Cinco cursos foram baixados e processados: `engenharia_civil`, `engenharia_de_alimentos`, `engenharia_da_computacao`, `engenharia_de_controle_e_automacao`, `engenharia_de_producao`.
- Q22 de Engenharia de Controle e Automacao deve ficar `fora_escopo`, pois as alternativas dependem de circuito/equacao booleana visual extraida como texto (`ABCD Motor`).
- Engenharia Civil Q17 e Q36 devem ficar `fora_escopo`: Q17 depende de fórmula matemática visual mal preservada na extração; Q36 depende de bloco estruturado de pseudocódigo.
- Rodapes de cursos com nome composto, como `18 Engenharia Civil` e `34 Engenharia de Alimentos`, passaram a ser removidos das alternativas.
- Auditoria geral apos o lote: 405 `completa`, 241 `fora_escopo`, 0 `incompleta`.
- Estado de 2023 naquele momento historico: 17 cursos processados e 11 cursos pendentes. O estado atual esta no fechamento de 2026-05-14.

## Atualizacao de fechamento - 2026-05-14

- Os 11 cursos restantes de 2023 foram baixados e processados: `engenharia_eletrica`, `engenharia_florestal`, `engenharia_mecanica`, `engenharia_quimica`, `zootecnia`, `tecnologia_em_agronegocio`, `tecnologia_em_estetica_e_cosmetico`, `tecnologia_em_gestao_ambiental`, `tecnologia_em_gestao_hospitalar`, `tecnologia_em_radiologia`, `tecnologia_em_seguranca_do_trabalho`.
- 2023 agora esta com 28 cursos processados, 0 cursos pendentes, 668 `completa`, 396 `fora_escopo` e 0 `incompleta` apos a revisao em modo estudante.
- Naquele momento, a ultima conferencia com olho humano era `engenharia_civil`. Depois dela, os demais cursos foram refinados por auditoria automatica e regras conservadoras; o marco humano foi atualizado depois para `fisioterapia`.
- `scripts/parser/processar_lote_2023.py` agora lista todos os 28 cursos em `CURSOS_ATUAIS_2023` e deixa `CURSOS_PENDENTES_2023` vazio.
- `scripts/parser/pos_processar_exibicao.py` ganhou reforcos para descartar graficos de nivel/tempo, modelo de reator com conservacao de massa e lei de Fick, infografico, mapas, esquemas e figuras textualmente referenciadas.
- Registro detalhado: `docs/RETOMADA_2026-05-14_FECHAMENTO_2023.md`.

## Atualizacao de revisao em modo estudante - 2026-05-14

- Foi feita uma revisao das questoes `completa` como se um estudante fosse tentar resolver sem consultar o PDF.
- Foram movidas para `fora_escopo`: `engenharia_da_computacao` Q18, `engenharia_de_producao` Q38, `engenharia_florestal` Q29, `engenharia_quimica` Q16 e `engenharia_quimica` Q25.
- Motivos: notacao matematica quebrada, esquema de ambientes, folha representada visualmente, fluxograma e equacoes/layout matematico nao confiavel.
- Foram removidos rodapes soltos de alternativas com nome do curso/numero da pagina e restos de referencias `Disponivel em:`/`Acesso em:`.
- Auditoria final atualizada: 668 `completa`, 396 `fora_escopo`, 0 `incompleta`.
- Varreduras finais: 0 artefatos em completas, 0 caracteres invalidos, 0 padroes visuais fortes nao justificados e 0 rodapes finais candidatos.

## Atualizacao de revisao humana - 2026-05-15

- O usuario informou que a revisao com olho humano avancou ate `fisioterapia` inclusive, seguindo a ordem de `scripts/parser/processar_lote_2023.py`.
- Os cursos apos `fisioterapia` permanecem como extraidos/refinados por auditoria automatica e regras conservadoras, devendo receber olho humano amostral antes da carga definitiva no banco.
- Auditoria geral naquele momento: 28 cursos, 668 `completa`, 396 `fora_escopo`, 0 `incompleta` e 0 cursos pendentes.

## Atualizacao de escopo humano - 2026-05-15

- Foi aplicada a lista humana de questoes fora do escopo dos cursos de `engenharia_civil` ate `fisioterapia`.
- A lista ficou registrada em `scripts/parser/escopo_manual_2023.py`, e `auditar_qualidade.py` agora falha se alguma questao dessa lista voltar para `completa`.
- Os cursos revisados foram reprocessados e a planilha de conferencia foi atualizada.
- Auditoria geral apos a aplicacao: 28 cursos, 655 `completa`, 409 `fora_escopo`, 0 `incompleta` e 0 cursos pendentes.

## Atualizacao do banco - 2026-05-16

- O banco local `enade_postgres` foi recriado/ajustado e carregado com os 28 cursos de 2023.
- `criado_em` foi removido das tabelas `PROVA`, `QUESTAO_STAGING` e `QUESTAO`, pois a data de exportacao nao e necessaria para o projeto.
- `CURSO` ganhou `SLUG`, mantendo nomes de exibicao com acentos e capitalizacao correta.
- A limpeza de texto corrigiu ocorrencias recorrentes de OCR em campos exibidos: `insufi cientes`, `legislati vas` e `politi ca`.
- Validacao do banco: `questao_staging` 1064, `questao` 651, `gabarito` 651 e `alternativa` 3230.
- Validacao final: 0 questoes finais fora do staging `COMPLETA`, 0 colunas `criado_em` restantes e 0 ocorrencias dos problemas de OCR nos campos finais.
