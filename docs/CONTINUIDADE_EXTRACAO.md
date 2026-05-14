# Continuidade da Extração ENADE

Data deste registro: 2026-05-07.

Este documento resume o estado atual do trabalho para que outro chat consiga continuar sem depender do histórico da conversa.

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

Resumo após a última auditoria:

| Curso | Completas | Fora de escopo | Incompletas | Observação |
|---|---:|---:|---:|---|
| Agronomia | 29 | 9 | 0 | Q6 fora do escopo por regra do projeto |
| Arquitetura e Urbanismo | 15 | 23 | 0 | Q6 fora do escopo por regra do projeto |
| Biomedicina | 20 | 18 | 0 | Q6 fora do escopo por regra do projeto |
| Enfermagem | 28 | 10 | 0 | Q6 fora do escopo por regra do projeto |
| Engenharia Ambiental | 24 | 14 | 0 | Q6 fora do escopo por regra do projeto |
| Engenharia Civil | 18 | 20 | 0 | Q17 e Q36 fora do escopo por fórmula/pseudocódigo visual |
| Engenharia de Alimentos | 23 | 15 | 0 | Q6 fora do escopo por regra do projeto |
| Engenharia da Computação | 23 | 15 | 0 | Q6 fora do escopo por regra do projeto |
| Engenharia de Controle e Automação | 14 | 24 | 0 | Q22 fora do escopo por circuito/equação visual |
| Engenharia de Produção | 13 | 25 | 0 | Q6 fora do escopo por regra do projeto |
| Farmácia | 26 | 12 | 0 | Q6 fora do escopo por regra do projeto |
| Fisioterapia | 26 | 12 | 0 | Q6 fora do escopo por regra do projeto |
| Fonoaudiologia | 28 | 10 | 0 | Q6 fora do escopo por regra do projeto |
| Medicina | 30 | 8 | 0 | Parser ajustado para alternativas A-D; Q10 fora do escopo por tabela extraída como texto |
| Medicina Veterinária | 28 | 10 | 0 | Q6 fora do escopo por regra do projeto |
| Nutrição | 31 | 7 | 0 | Q6 fora do escopo por regra do projeto |
| Odontologia | 29 | 9 | 0 | Q23, Q25 e Q26 corrigidas como textuais; Q26 anulada no gabarito oficial |

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

1. Revisar manualmente os cursos novos:
   - Farmácia
   - Fisioterapia
   - Fonoaudiologia
   - Medicina
   - Medicina Veterinária
   - Nutrição
   - Odontologia
   - Engenharia Civil
   - Engenharia de Alimentos
   - Engenharia da Computação
   - Engenharia de Controle e Automação
   - Engenharia de Produção
2. Só depois carregar no banco.
3. Quando 2023 estiver estável, replicar o fluxo para anos anteriores, começando por 2022 ou 2021 antes de ir até 2015.

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
python scripts/parser/auditar_qualidade.py --falhar-se-problema
python scripts/parser/processar_lote_2023.py --listar
python scripts/parser/processar_lote_2023.py --pendentes --listar
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
- Estado de 2023: 17 cursos processados e 11 cursos pendentes.
