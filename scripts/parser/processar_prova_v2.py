
import re
import json
import argparse
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from pos_processar_exibicao import limpar_texto_exibicao, classificar_status_exibicao

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader


SEQUENCIAS_ALTERNATIVAS: Tuple[Tuple[str, ...], ...] = (
    ("A", "B", "C", "D", "E"),
    ("A", "B", "C", "D"),
)


# =========================================================
# UTILIDADES
# =========================================================
def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def normalizar_texto(texto: str) -> str:
    texto = texto.replace("\r", "\n")
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def ler_pdf(caminho_pdf: Path) -> str:
    if not caminho_pdf.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")

    reader = PdfReader(str(caminho_pdf))
    paginas = []

    for pagina in reader.pages:
        texto = pagina.extract_text() or ""
        paginas.append(texto)

    return "\n".join(paginas)


def detectar_questoes_em_paginas_com_imagem(
    caminho_pdf: Path,
    numeros_validos: Set[int]
) -> Set[int]:
    reader = PdfReader(str(caminho_pdf))
    questoes_com_imagem = set()

    for pagina in reader.pages:
        try:
            imagens = list(pagina.images)
        except Exception:
            imagens = []

        if not imagens:
            continue

        texto = pagina.extract_text() or ""
        numeros_pagina = set()

        for match in re.finditer(r"QUEST", texto, flags=re.IGNORECASE):
            trecho = texto[match.start():match.start() + 35]
            if "DISCURSIVA" in trecho.upper():
                continue

            numero_match = re.search(r"\d{1,3}", trecho)
            if not numero_match:
                continue

            numero = int(numero_match.group(0))
            if numero in numeros_validos:
                numeros_pagina.add(numero)

        # Evita punir uma questao textual que divide pagina com outra visual.
        if len(numeros_pagina) == 1:
            questoes_com_imagem.update(numeros_pagina)

    return questoes_com_imagem


def auto_encontrar_pdf(pasta_pdfs: Path, marcador: str) -> Path:
    candidatos = sorted(pasta_pdfs.glob(f"*{marcador}*.pdf"))
    if not candidatos:
        raise FileNotFoundError(
            f"Nenhum PDF com '{marcador}' encontrado em {pasta_pdfs}"
        )
    return candidatos[0]


def extrair_tokens_contexto(caminho_pdf: Path) -> List[str]:
    stopwords = {
        "pv", "gb", "enade", "prova", "gabarito", "caderno", "componente",
        "especifico", "geral", "curso", "provao", "oficial", "versao"
    }

    partes = re.split(r"[^a-zA-Z0-9]+", slugify(caminho_pdf.stem))
    tokens = []

    for p in partes:
        if not p:
            continue
        if p.isdigit():
            continue
        if p in stopwords:
            continue
        if len(p) < 4:
            continue
        tokens.append(p)

    return tokens


# =========================================================
# LIMPEZA DE RUÍDO
# =========================================================
def remover_linhas_ruins(texto: str, context_tokens: List[str]) -> str:
    linhas_filtradas = []
    context_slug = "_".join(context_tokens)

    for linha in texto.splitlines():
        original = linha
        l = linha.strip()
        l_slug = slugify(l)

        if not l:
            linhas_filtradas.append("")
            continue

        if "validinep" in l_slug:
            continue

        if re.fullmatch(r"\*.*\*", l):
            continue

        if re.fullmatch(r"logo", l_slug):
            continue

        if re.fullmatch(r"materia", l_slug):
            continue

        if re.fullmatch(r"\d{1,3}\s+materia", l_slug):
            continue

        if re.fullmatch(r"materia\s+\d{1,3}", l_slug):
            continue

        if re.fullmatch(r"\d{1,3}", l):
            continue

        remover = False
        if context_slug:
            if re.fullmatch(rf"{re.escape(context_slug)}[_\s]+\d{{1,3}}", l_slug):
                remover = True
            if re.fullmatch(rf"\d{{1,3}}[_\s]+{re.escape(context_slug)}", l_slug):
                remover = True
            if (
                re.fullmatch(r"\d{1,3}[_\s]+[a-z0-9_\s]+", l_slug)
                and all(token in l_slug for token in context_tokens)
            ):
                remover = True
            if (
                re.fullmatch(r"[a-z0-9_\s]+[_\s]+\d{1,3}", l_slug)
                and all(token in l_slug for token in context_tokens)
            ):
                remover = True

        for token in context_tokens:
            if re.fullmatch(rf"{re.escape(token)}[_\s]+\d{{1,3}}", l_slug):
                remover = True
                break
            if re.fullmatch(rf"\d{{1,3}}[_\s]+{re.escape(token)}", l_slug):
                remover = True
                break

        if remover:
            continue

        linhas_filtradas.append(original)

    texto_limpo = "\n".join(linhas_filtradas)
    texto_limpo = re.sub(r"\n{3,}", "\n\n", texto_limpo)
    return texto_limpo.strip()


# =========================================================
# GABARITO
# =========================================================
def extrair_gabarito(texto_gb: str) -> Dict[int, Optional[str]]:
    texto = normalizar_texto(texto_gb).upper()
    gabarito: Dict[int, Optional[str]] = {}

    for num_str in re.findall(r"\bQUEST(?:ÃO|AO)\s*(\d{1,3})\s+ANULADA\b", texto):
        num = int(num_str)
        if 1 <= num <= 100:
            gabarito[num] = None

    pares = re.findall(r"\b(\d{1,3})\s*[-–:.)]?\s*([ABCDE])\b", texto)

    for num_str, letra in pares:
        num = int(num_str)
        if 1 <= num <= 100 and num not in gabarito:
            gabarito[num] = letra

    if len(gabarito) < 10:
        tokens = re.findall(r"\b\d{1,3}\b|\b[ABCDE]\b", texto)
        for i in range(len(tokens) - 1):
            atual = tokens[i]
            prox = tokens[i + 1]

            if atual.isdigit() and prox in "ABCDE":
                num = int(atual)
                if 1 <= num <= 100 and num not in gabarito:
                    gabarito[num] = prox

    return dict(sorted(gabarito.items()))


# =========================================================
# DIVISÃO EM BLOCOS
# =========================================================
def dividir_blocos_questao(texto_prova: str) -> List[str]:
    texto = normalizar_texto(texto_prova)

    padrao = re.compile(r"(QUEST(?:ÃO|AO)\s*\d{1,3})", flags=re.IGNORECASE)
    matches = list(padrao.finditer(texto))

    blocos = []
    for i, match in enumerate(matches):
        inicio = match.start()
        fim = matches[i + 1].start() if i + 1 < len(matches) else len(texto)
        blocos.append(texto[inicio:fim].strip())

    return blocos


def extrair_numero_bloco(bloco: str) -> Optional[int]:
    m = re.search(r"QUEST(?:ÃO|AO)\s*(\d{1,3})", bloco, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def limpar_cabecalho_questao(bloco: str, context_tokens: List[str]) -> str:
    texto = bloco.strip()

    texto = re.sub(
        r"^\s*QUEST(?:ÃO|AO)\s*\d{1,3}\s*",
        "",
        texto,
        flags=re.IGNORECASE
    ).strip()

    texto = remover_linhas_ruins(texto, context_tokens)
    texto = normalizar_texto(texto)
    return texto


# =========================================================
# PARSER DE ALTERNATIVAS
# =========================================================
def encontrar_corte_alternativas(texto: str) -> Optional[int]:
    padroes = [
        r"assinale\s+a\s+op(?:ç|c)[aã]o\s+correta\b",
        r"assinale\s+a\s+alternativa\s+correta\b",
        r"assinale\s+a\s+alternativa\s+incorreta\b",
        r"[ée]\s+correto\s+apenas\s+o\s+que\s+se\s+afirma\s+em\b",
        r"[ée]\s+incorreto\s+apenas\s+o\s+que\s+se\s+afirma\s+em\b",
        r"[ée]\s+correto\s+o\s+que\s+se\s+afirma\s+em\b",
        r"[ée]\s+incorreto\s+o\s+que\s+se\s+afirma\s+em\b",
        r"[ée]\s+correto\s+afirmar\s+que\b",
        r"[ée]\s+incorreto\s+afirmar\s+que\b",
        r"assinale\s+a\s+op(?:ç|c)[aã]o\s+que\s+apresenta\b",
        r"assinale\s+a\s+op(?:ç|c)[aã]o\s+que\s+indica\b",
        r"considere\s+as\s+afirmativas\b",
    ]

    ultimo_fim = None
    for padrao in padroes:
        for m in re.finditer(padrao, texto, flags=re.IGNORECASE | re.DOTALL):
            ultimo_fim = m.end()

    return ultimo_fim


def normalizar_trecho_alternativas(texto: str) -> str:
    texto = texto.replace("\r", "\n")
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)

    texto = re.sub(r"(?m)^\s*([ABCDE])\s*[\)\.\-:]\s*", r"\1 ", texto)
    texto = re.sub(r"(?m)^\s*([ABCDE])\s+(?=\S)", r"\1 ", texto)

    texto = re.sub(
        r"(?<!\n)([.!?;])\s+([ABCDE])\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9\(])",
        r"\1\n\2 ",
        texto
    )

    texto = re.sub(
        r"(?<!\n)([.!?;])\s+([ABCDE])[\)\.\-:]\s*(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9\(])",
        r"\1\n\2 ",
        texto
    )

    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def localizar_marcadores_alternativas(texto: str):
    padrao = re.compile(r"(?m)^\s*([ABCDE])\s+")
    return list(padrao.finditer(texto))


def localizar_sequencia_alternativas(matches) -> Tuple[Optional[int], Tuple[str, ...]]:
    letras = [m.group(1) for m in matches]

    for sequencia in SEQUENCIAS_ALTERNATIVAS:
        tamanho = len(sequencia)
        for i in range(len(letras) - tamanho + 1):
            if tuple(letras[i:i + tamanho]) == sequencia:
                return i, sequencia

    return None, tuple()


def encontrar_inicio_sequencia_alternativas(texto: str) -> Tuple[Optional[int], Tuple[str, ...]]:
    matches = localizar_marcadores_alternativas(texto)
    indice_inicio, sequencia = localizar_sequencia_alternativas(matches)

    if indice_inicio is None:
        return None, tuple()

    return matches[indice_inicio].start(), sequencia


def separar_trecho_pos_alternativas(conteudo: str) -> Tuple[str, str]:
    padrao_codigo_numerado = re.compile(
        r"(?m)\n\s*(1\s+(?:inicio|início)\b.*)$",
        flags=re.IGNORECASE | re.DOTALL
    )
    match = padrao_codigo_numerado.search(conteudo)
    if not match:
        return conteudo, ""

    trecho_pos = match.group(1).strip()
    linhas_codigo = [
        linha for linha in trecho_pos.splitlines()
        if re.match(r"\s*\d{1,2}\s+\S+", linha)
    ]
    texto_codigo = " ".join(linhas_codigo).lower()
    palavras_codigo = [
        "inicio",
        "início",
        "variavel",
        "variável",
        "para",
        "proximo",
        "próximo",
        "fim",
        "fimse",
        "escrever",
        "ler",
    ]

    if len(linhas_codigo) < 4:
        return conteudo, ""

    if not any(palavra in texto_codigo for palavra in palavras_codigo):
        return conteudo, ""

    trecho_pos = re.split(
        r"(?im)^\s*(?:\*R\d+|VALIDINEP|[A-Za-zÀ-ÿ ]+\s+\d+)\b",
        trecho_pos,
        maxsplit=1
    )[0].strip()
    conteudo_alt = conteudo[:match.start()].strip()
    return conteudo_alt, trecho_pos


def inserir_trecho_pos_alternativas(enunciado: str, trecho_pos: str) -> str:
    if not trecho_pos:
        return enunciado

    match = re.search(
        r"pseudoc[oó]digo apresentado a seguir\.",
        enunciado,
        flags=re.IGNORECASE
    )
    if match:
        return (
            enunciado[:match.end()]
            + "\n\n"
            + trecho_pos
            + "\n\n"
            + enunciado[match.end():].lstrip()
        )

    return f"{enunciado}\n\n{trecho_pos}".strip()


def extrair_alternativas_do_tail(
    tail: str,
    context_tokens: List[str]
) -> Tuple[Dict[str, str], str, Tuple[str, ...], str]:
    tail = normalizar_trecho_alternativas(tail)
    matches = localizar_marcadores_alternativas(tail)

    indice_inicio, sequencia = localizar_sequencia_alternativas(matches)

    if indice_inicio is None:
        return {}, tail, tuple(), ""

    alternativas = {}
    seq = matches[indice_inicio:indice_inicio + len(sequencia)]
    trecho_pos_alternativas = ""

    for i, match in enumerate(seq):
        letra = match.group(1)
        inicio = match.end()
        fim = seq[i + 1].start() if i + 1 < len(seq) else len(tail)
        conteudo = tail[inicio:fim].strip()
        if i == len(seq) - 1:
            conteudo, trecho_pos_alternativas = separar_trecho_pos_alternativas(conteudo)
        conteudo = remover_linhas_ruins(conteudo, context_tokens)
        conteudo = normalizar_texto(conteudo)
        alternativas[letra] = conteudo

    trecho_pos_alternativas = remover_linhas_ruins(trecho_pos_alternativas, context_tokens)
    trecho_pos_alternativas = normalizar_texto(trecho_pos_alternativas)
    return alternativas, tail, sequencia, trecho_pos_alternativas


def construir_candidato_parse(
    enunciado: str,
    tail: str,
    strategy: str,
    context_tokens: List[str]
) -> Dict[str, object]:
    enunciado = remover_linhas_ruins(enunciado, context_tokens)
    enunciado = normalizar_texto(enunciado)

    alternativas, tail_norm, alternativas_esperadas, trecho_pos_alternativas = extrair_alternativas_do_tail(
        tail,
        context_tokens
    )
    completo = bool(alternativas_esperadas) and all(
        letra in alternativas and alternativas[letra]
        for letra in alternativas_esperadas
    )

    return {
        "enunciado": enunciado,
        "alternativas": alternativas,
        "alternativas_esperadas": list(alternativas_esperadas),
        "trecho_pos_alternativas": trecho_pos_alternativas,
        "completo": completo,
        "strategy": strategy,
        "tail_normalizado": tail_norm
    }


def parsear_bloco_questao(bloco: str, context_tokens: List[str]) -> Dict[str, object]:
    texto = limpar_cabecalho_questao(bloco, context_tokens)
    candidatos = []

    corte = encontrar_corte_alternativas(texto)
    if corte is not None:
        candidatos.append(
            construir_candidato_parse(
                texto[:corte],
                texto[corte:],
                "corte_por_comando",
                context_tokens
            )
        )

    texto_norm = normalizar_trecho_alternativas(texto)
    inicio_seq, _ = encontrar_inicio_sequencia_alternativas(texto_norm)
    if inicio_seq is not None:
        candidatos.append(
            construir_candidato_parse(
                texto_norm[:inicio_seq],
                texto_norm[inicio_seq:],
                "sequencia_alternativas_global",
                context_tokens
            )
        )

    candidatos.append(
        construir_candidato_parse(
            "",
            texto,
            "tail_total",
            context_tokens
        )
    )

    melhor = max(
        candidatos,
        key=lambda c: (
            len(c["alternativas"]),
            int(c["completo"]),
            len(c["enunciado"])
        )
    )

    return melhor


def contar_alternativas(bloco: str, context_tokens: List[str]) -> int:
    partes = parsear_bloco_questao(bloco, context_tokens)
    return len(partes["alternativas"])


# =========================================================
# SCORE DO BLOCO
# =========================================================
def pontuar_bloco(bloco: str, context_tokens: List[str]) -> int:
    texto = bloco.lower()
    score = 0

    partes = parsear_bloco_questao(bloco, context_tokens)
    qtd_alts = len(partes["alternativas"])

    score += qtd_alts * 20

    if partes["completo"]:
        score += 20

    tamanho = len(bloco)
    if tamanho > 400:
        score += 5
    if tamanho > 800:
        score += 5

    palavras_ruins = [
        "questionário de percepção",
        "questionario de percepção",
        "questionario de percepcao",
        "impressão sobre a prova",
        "avaliacao da prova",
        "avaliação da prova",
        "componente específico: discursiva",
        "componente especifico: discursiva",
        "rascunho",
        "redija",
        "texto dissertativo",
    ]

    for p in palavras_ruins:
        if p in texto:
            score -= 30

    return score


# =========================================================
# ESCOLHA DOS MELHORES BLOCOS
# =========================================================
def selecionar_melhores_blocos(
    blocos: List[str],
    numeros_gabarito: Set[int],
    context_tokens: List[str]
):
    candidatos = {}

    for bloco in blocos:
        numero = extrair_numero_bloco(bloco)
        if numero is None:
            continue

        if numero not in numeros_gabarito:
            continue

        partes = parsear_bloco_questao(bloco, context_tokens)
        score = pontuar_bloco(bloco, context_tokens)

        candidatos.setdefault(numero, []).append({
            "numero": numero,
            "score": score,
            "qtd_alternativas": len(partes["alternativas"]),
            "alternativas_esperadas": partes["alternativas_esperadas"],
            "alternativas_completas": partes["completo"],
            "strategy": partes["strategy"],
            "tamanho": len(bloco),
            "texto": bloco,
        })

    melhores = {}
    debug = {}

    for numero in sorted(numeros_gabarito):
        lista = candidatos.get(numero, [])
        if not lista:
            continue

        lista_ordenada = sorted(
            lista,
            key=lambda x: (
                x["score"],
                x["qtd_alternativas"],
                int(x["alternativas_completas"]),
                x["tamanho"]
            ),
            reverse=True
        )

        melhores[numero] = lista_ordenada[0]["texto"]
        debug[numero] = lista_ordenada

    return melhores, debug


# =========================================================
# SAÍDAS
# =========================================================
def montar_confianca(score_bloco: int, alternativas_completas: bool) -> str:
    if alternativas_completas and score_bloco >= 130:
        return "alta"
    if alternativas_completas:
        return "media"
    return "baixa"


def salvar_amostra(arquivo: Path, questoes: List[Dict[str, object]], limite: int = 5):
    with open(arquivo, "w", encoding="utf-8") as f:
        for q in questoes[:limite]:
            f.write("=" * 100 + "\n")
            f.write(f"QUESTÃO {q['numero']}\n")
            f.write(f"GABARITO: {q['gabarito']}\n")
            f.write(f"STATUS: {q['status']}\n")
            f.write(f"CONFIANÇA: {q['confianca']}\n")
            f.write(f"ESTRATÉGIA: {q['parse_strategy']}\n")
            f.write(f"ALTERNATIVAS ESPERADAS: {q.get('alternativas_esperadas', [])}\n")
            f.write(f"ALTERNATIVAS COMPLETAS: {q['alternativas_completas']}\n")
            if q.get("observacao"):
                f.write(f"OBSERVAÇÃO: {q['observacao']}\n")
            f.write("\n")

            f.write("ENUNCIADO:\n")
            f.write((q["enunciado"] or "[vazio]") + "\n\n")

            f.write("ALTERNATIVAS:\n")
            if q["alternativas"]:
                for letra, valor in q["alternativas"].items():
                    f.write(f"{letra}) {valor}\n")
            else:
                f.write("Nenhuma alternativa separada.\n")

            f.write("\nTEXTO BRUTO:\n")
            f.write(q["texto_bruto"] + "\n\n")


# =========================================================
# PROCESSAMENTO PRINCIPAL
# =========================================================
def processar(pdf_prova: Path, pdf_gabarito: Path, pasta_output: Path):
    pasta_output.mkdir(parents=True, exist_ok=True)

    prefixo = slugify(pdf_prova.stem)
    context_tokens = extrair_tokens_contexto(pdf_prova)

    arq_saida_json = pasta_output / f"{prefixo}_questoes.json"
    arq_saida_debug = pasta_output / f"{prefixo}_debug_blocos.json"
    arq_relatorio = pasta_output / f"{prefixo}_relatorio.txt"
    arq_amostra = pasta_output / f"{prefixo}_amostra.txt"
    arq_quarentena = pasta_output / f"{prefixo}_quarentena.json"

    print("Lendo prova...")
    texto_prova = ler_pdf(pdf_prova)

    print("Lendo gabarito...")
    texto_gabarito = ler_pdf(pdf_gabarito)

    print("Extraindo gabarito...")
    gabarito = extrair_gabarito(texto_gabarito)
    if not gabarito:
        raise ValueError("Não foi possível extrair o gabarito do PDF GB.")

    numeros_gabarito = set(gabarito.keys())
    print(f"Gabarito encontrado com {len(gabarito)} questões.")

    print("Detectando imagens por pagina...")
    questoes_em_paginas_com_imagem = detectar_questoes_em_paginas_com_imagem(
        pdf_prova,
        numeros_gabarito
    )
    if questoes_em_paginas_com_imagem:
        print(f"Questoes em paginas com imagem: {sorted(questoes_em_paginas_com_imagem)}")

    print("Dividindo blocos da prova...")
    blocos = dividir_blocos_questao(texto_prova)
    print(f"Blocos encontrados: {len(blocos)}")

    print("Selecionando melhores blocos...")
    melhores_blocos, debug = selecionar_melhores_blocos(
        blocos,
        numeros_gabarito,
        context_tokens
    )

    questoes_final = []
    quarentena = []
    faltando = []

    for numero in sorted(numeros_gabarito):
        bloco = melhores_blocos.get(numero)

        if not bloco:
            faltando.append(numero)
            registro_faltante = {
                "numero": numero,
                "gabarito": gabarito[numero],
                "status": "nao_encontrada"
            }
            quarentena.append(registro_faltante)
            continue

        partes = parsear_bloco_questao(bloco, context_tokens)
        score_bloco = pontuar_bloco(bloco, context_tokens)

        status = "completa" if partes["completo"] else "incompleta"
        confianca = montar_confianca(score_bloco, partes["completo"])

        alternativas_limpas = {
            letra: limpar_texto_exibicao(texto_alt)
            for letra, texto_alt in (partes["alternativas"] or {}).items()
        }

        enunciado_limpo = limpar_texto_exibicao(str(partes["enunciado"]))
        trecho_pos_alternativas = str(partes.get("trecho_pos_alternativas") or "")
        if trecho_pos_alternativas:
            enunciado_limpo = inserir_trecho_pos_alternativas(
                enunciado_limpo,
                trecho_pos_alternativas
            )
        status, observacao = classificar_status_exibicao(status, bloco)
        if gabarito[numero] is None:
            observacao_anulada = "QUESTAO ANULADA NO GABARITO OFICIAL"
            observacao = (
                f"{observacao}; {observacao_anulada}"
                if observacao
                else observacao_anulada
            )
        if numero in questoes_em_paginas_com_imagem:
            status = "fora_escopo"
            observacao = "QUESTAO EM PAGINA COM ELEMENTO VISUAL"
        if numero == 6:
            status = "fora_escopo"
            observacao = "QUESTAO 6 FORA DO ESCOPO POR REGRA DO PROJETO"

        registro = {
            "numero": numero,
            "gabarito": gabarito[numero],
            "status": status,
            "confianca": confianca,
            "score_bloco": score_bloco,
            "parse_strategy": partes["strategy"],
            "enunciado": enunciado_limpo,
            "alternativas": alternativas_limpas,
            "alternativas_esperadas": partes["alternativas_esperadas"],
            "trecho_pos_alternativas": trecho_pos_alternativas,
            "alternativas_completas": partes["completo"],
            "texto_bruto": bloco,
            "observacao": observacao,
        }

        questoes_final.append(registro)

        if status != "completa":
            quarentena.append(registro)

    completas = [q["numero"] for q in questoes_final if q["status"] == "completa"]
    incompletas = [q["numero"] for q in questoes_final if q["status"] == "incompleta"]
    fora_escopo = [q["numero"] for q in questoes_final if q["status"] == "fora_escopo"]

    salvar_amostra(arq_amostra, questoes_final, limite=5)

    with open(arq_saida_json, "w", encoding="utf-8") as f:
        json.dump(questoes_final, f, ensure_ascii=False, indent=2)

    with open(arq_saida_debug, "w", encoding="utf-8") as f:
        json.dump(debug, f, ensure_ascii=False, indent=2)

    with open(arq_quarentena, "w", encoding="utf-8") as f:
        json.dump(quarentena, f, ensure_ascii=False, indent=2)

    with open(arq_relatorio, "w", encoding="utf-8") as f:
        f.write("RELATÓRIO DE PROCESSAMENTO V2\n")
        f.write("=" * 60 + "\n")
        f.write(f"PDF prova: {pdf_prova.name}\n")
        f.write(f"PDF gabarito: {pdf_gabarito.name}\n")
        f.write(f"Prefixo de saída: {prefixo}\n")
        f.write(f"Tokens de contexto: {context_tokens}\n\n")

        f.write(f"Questões no gabarito: {len(gabarito)}\n")
        f.write(f"Questões encontradas: {len(questoes_final)}\n")
        f.write(f"Questões completas: {len(completas)}\n")
        f.write(f"Questões incompletas: {len(incompletas)}\n")
        f.write(f"Questões fora de escopo: {len(fora_escopo)}\n")
        f.write(f"Questões faltando: {len(faltando)}\n\n")

        f.write(f"Completas: {completas}\n")
        f.write(f"Incompletas: {incompletas}\n")
        f.write(f"Fora de escopo: {fora_escopo}\n")
        f.write(f"Faltando: {faltando}\n")

    print("\nPROCESSAMENTO FINALIZADO")
    print(f"Questões no gabarito: {len(gabarito)}")
    print(f"Questões encontradas: {len(questoes_final)}")
    print(f"Questões completas: {len(completas)}")
    print(f"Questões incompletas: {len(incompletas)}")
    print(f"Questões fora de escopo: {len(fora_escopo)}")
    print(f"Questões faltando: {len(faltando)}")
    print("\nArquivos gerados:")
    print(f"- {arq_saida_json}")
    print(f"- {arq_saida_debug}")
    print(f"- {arq_relatorio}")
    print(f"- {arq_amostra}")
    print(f"- {arq_quarentena}")


def main():
    root = Path(__file__).resolve().parents[2]
    pasta_pdfs = root / "pdfs"

    parser = argparse.ArgumentParser(
        description="Processa prova ENADE e gabarito em modo mais genérico."
    )
    parser.add_argument("--pv", type=str, help="Caminho do PDF da prova")
    parser.add_argument("--gb", type=str, help="Caminho do PDF do gabarito")
    parser.add_argument(
        "--out-dir",
        type=str,
        help="Pasta de saída. Se não informar, salva automaticamente em output/v2/<ano_curso>"
    )
    args = parser.parse_args()

    pdf_prova = Path(args.pv) if args.pv else auto_encontrar_pdf(pasta_pdfs, "PV")
    pdf_gabarito = Path(args.gb) if args.gb else auto_encontrar_pdf(pasta_pdfs, "GB")

    if args.out_dir:
        pasta_output = Path(args.out_dir)
    else:
        nome_base = slugify(pdf_prova.stem)
        nome_base = nome_base.replace("_pv_", "_").replace("_gb_", "_")
        pasta_output = root / "output" / "v2" / nome_base

    print(f"Pasta de saída: {pasta_output}")
    processar(pdf_prova, pdf_gabarito, pasta_output)


if __name__ == "__main__":
    main()
