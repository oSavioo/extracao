import re
import json
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader


# =========================
# CONFIGURAÇÃO DE CAMINHOS
# =========================
ROOT = Path(__file__).resolve().parents[2]
PASTA_PDFS = ROOT / "pdfs"
PASTA_OUTPUT = ROOT / "output"

PDF_PROVA = PASTA_PDFS / "2023_PV_agronomia.pdf"
PDF_GABARITO = PASTA_PDFS / "2023_GB_agronomia.pdf"

ARQ_SAIDA_JSON = PASTA_OUTPUT / "questoes_extraidas_2023_agronomia.json"
ARQ_SAIDA_DEBUG = PASTA_OUTPUT / "debug_blocos_2023_agronomia.json"
ARQ_RELATORIO = PASTA_OUTPUT / "relatorio_2023_agronomia.txt"
ARQ_AMOSTRA = PASTA_OUTPUT / "amostra_questoes_2023_agronomia.txt"


# =========================
# LEITURA PDF
# =========================
def extrair_texto_pdf(caminho_pdf: Path) -> str:
    if not caminho_pdf.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")

    reader = PdfReader(str(caminho_pdf))
    paginas = []

    for pagina in reader.pages:
        texto = pagina.extract_text() or ""
        paginas.append(texto)

    return "\n".join(paginas)


# =========================
# NORMALIZAÇÃO GERAL
# =========================
def normalizar_texto(texto: str) -> str:
    texto = texto.replace("\r", "\n")
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def remover_linhas_ruins(texto: str) -> str:
    linhas_filtradas = []

    for linha in texto.splitlines():
        l = linha.strip()

        if not l:
            linhas_filtradas.append("")
            continue

        if "VALIDINEP" in l.upper():
            continue

        if re.fullmatch(r"\*.*\*", l):
            continue

        if re.fullmatch(r"LOGO", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"MAT[ÉE]RIA", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"\d+\s+MAT[ÉE]RIA", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"Agronomia\s+\d+", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"\d+\s+Agronomia", l, flags=re.IGNORECASE):
            continue

        linhas_filtradas.append(linha)

    texto_limpo = "\n".join(linhas_filtradas)
    texto_limpo = re.sub(r"\n{3,}", "\n\n", texto_limpo)
    return texto_limpo.strip()


# =========================
# EXTRAÇÃO DO GABARITO
# =========================
def extrair_gabarito(texto_gb: str) -> dict:
    texto = normalizar_texto(texto_gb).upper()
    gabarito = {}

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


# =========================
# DIVISÃO DA PROVA EM BLOCOS
# =========================
def dividir_blocos_questao(texto_prova: str) -> list:
    texto = normalizar_texto(texto_prova)

    padrao = re.compile(r"(QUEST(?:ÃO|AO)\s*\d{1,3})", flags=re.IGNORECASE)
    matches = list(padrao.finditer(texto))
    blocos = []

    for i, match in enumerate(matches):
        inicio = match.start()
        fim = matches[i + 1].start() if i + 1 < len(matches) else len(texto)
        bloco = texto[inicio:fim].strip()
        blocos.append(bloco)

    return blocos


def extrair_numero_bloco(bloco: str):
    m = re.search(r"QUEST(?:ÃO|AO)\s*(\d{1,3})", bloco, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


# =========================
# LIMPEZA DO BLOCO
# =========================
def limpar_cabecalho_questao(bloco: str) -> str:
    texto = bloco.strip()

    texto = re.sub(
        r"^\s*QUEST(?:ÃO|AO)\s*\d{1,3}\s*",
        "",
        texto,
        flags=re.IGNORECASE
    ).strip()

    texto = remover_linhas_ruins(texto)
    texto = normalizar_texto(texto)
    return texto


# =========================
# PARSER DE ALTERNATIVAS
# =========================
def encontrar_corte_alternativas(texto: str):
    padroes = [
        r"assinale\s+a\s+op(?:ç|c)[aã]o\s+correta\.",
        r"assinale\s+a\s+alternativa\s+correta\.",
        r"assinale\s+a\s+alternativa\s+incorreta\.",
        r"[ée]\s+correto\s+apenas\s+o\s+que\s+se\s+afi\s*rma\s+em",
        r"[ée]\s+incorreto\s+apenas\s+o\s+que\s+se\s+afi\s*rma\s+em",
        r"[ée]\s+correto\s+o\s+que\s+se\s+afi\s*rma\s+em",
        r"[ée]\s+incorreto\s+o\s+que\s+se\s+afi\s*rma\s+em",
        r"[ée]\s+correto\s+afi\s*rmar\s+que",
        r"[ée]\s+incorreto\s+afi\s*rmar\s+que",
        r"assinale\s+a\s+op(?:ç|c)[aã]o\s+que\s+apresenta",
    ]

    ultimo_fim = None

    for padrao in padroes:
        for m in re.finditer(padrao, texto, flags=re.IGNORECASE | re.DOTALL):
            ultimo_fim = m.end()

    return ultimo_fim


def normalizar_trecho_alternativas(tail: str) -> str:
    tail = tail.replace("\r", "\n")
    tail = tail.replace("\xa0", " ")
    tail = re.sub(r"[ \t]+", " ", tail)

    # Formatos como A), A., A-, A:
    tail = re.sub(r"(?m)^\s*([ABCDE])\s*[\)\.\-:]\s*", r"\1 ", tail)

    # Formato simples: A texto...
    tail = re.sub(r"(?m)^\s*([ABCDE])\s+", r"\1 ", tail)

    # Se colou tudo numa linha depois de ponto final
    tail = re.sub(
        r"(?<!\n)([\.!?])\s+([ABCDE])\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ])",
        r"\1\n\2 ",
        tail
    )

    tail = re.sub(r"\n{3,}", "\n\n", tail)
    return tail.strip()


def localizar_marcadores_alternativas(tail: str):
    padrao = re.compile(r"(?m)^\s*([ABCDE])\s+")
    return list(padrao.finditer(tail))


def extrair_alternativas_do_tail(tail: str) -> dict:
    tail = normalizar_trecho_alternativas(tail)
    matches = localizar_marcadores_alternativas(tail)

    if len(matches) < 5:
        return {}

    primeiras_letras = [m.group(1) for m in matches[:5]]

    if primeiras_letras != ["A", "B", "C", "D", "E"]:
        return {}

    alternativas = {}

    for i, match in enumerate(matches[:5]):
        letra = match.group(1)
        inicio = match.end()
        fim = matches[i + 1].start() if i + 1 < 5 else len(tail)
        conteudo = tail[inicio:fim].strip()
        conteudo = remover_linhas_ruins(conteudo)
        conteudo = normalizar_texto(conteudo)
        alternativas[letra] = conteudo

    return alternativas


def separar_enunciado_alternativas(bloco: str):
    texto = limpar_cabecalho_questao(bloco)
    corte = encontrar_corte_alternativas(texto)

    if corte is None:
        return {
            "enunciado": texto,
            "alternativas": {},
            "completo": False
        }

    enunciado = texto[:corte].strip()
    tail = texto[corte:].strip()

    alternativas = extrair_alternativas_do_tail(tail)

    return {
        "enunciado": enunciado,
        "alternativas": alternativas,
        "completo": all(
            letra in alternativas and alternativas[letra]
            for letra in ["A", "B", "C", "D", "E"]
        )
    }


def contar_alternativas(bloco: str) -> int:
    partes = separar_enunciado_alternativas(bloco)
    return len(partes["alternativas"])


# =========================
# SCORE DO BLOCO
# =========================
def pontuar_bloco(bloco: str) -> int:
    texto = bloco.lower()
    score = 0

    qtd_alts = contar_alternativas(bloco)
    score += qtd_alts * 20

    tamanho = len(bloco)
    if tamanho > 400:
        score += 5
    if tamanho > 800:
        score += 5

    if qtd_alts == 5:
        score += 20

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


# =========================
# ESCOLHA DOS MELHORES BLOCOS
# =========================
def selecionar_melhores_blocos(blocos: list, numeros_gabarito: set):
    candidatos = {}

    for bloco in blocos:
        numero = extrair_numero_bloco(bloco)
        if numero is None:
            continue

        if numero not in numeros_gabarito:
            continue

        score = pontuar_bloco(bloco)

        if numero not in candidatos:
            candidatos[numero] = []

        candidatos[numero].append({
            "numero": numero,
            "score": score,
            "qtd_alternativas": contar_alternativas(bloco),
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
            key=lambda x: (x["score"], x["qtd_alternativas"], x["tamanho"]),
            reverse=True
        )

        melhores[numero] = lista_ordenada[0]["texto"]
        debug[numero] = lista_ordenada

    return melhores, debug


# =========================
# PROCESSAMENTO PRINCIPAL
# =========================
def processar():
    PASTA_OUTPUT.mkdir(exist_ok=True)

    print("Lendo prova...")
    texto_prova = extrair_texto_pdf(PDF_PROVA)

    print("Lendo gabarito...")
    texto_gabarito = extrair_texto_pdf(PDF_GABARITO)

    print("Extraindo gabarito...")
    gabarito = extrair_gabarito(texto_gabarito)

    if not gabarito:
        raise ValueError("Não foi possível extrair o gabarito do PDF GB.")

    numeros_gabarito = set(gabarito.keys())
    print(f"Gabarito encontrado com {len(gabarito)} questões.")

    print("Dividindo blocos da prova...")
    blocos = dividir_blocos_questao(texto_prova)
    print(f"Blocos encontrados: {len(blocos)}")

    print("Selecionando melhores blocos...")
    melhores_blocos, debug = selecionar_melhores_blocos(blocos, numeros_gabarito)

    questoes_final = []
    faltando = []

    for numero in sorted(numeros_gabarito):
        bloco = melhores_blocos.get(numero)

        if not bloco:
            faltando.append(numero)
            continue

        partes = separar_enunciado_alternativas(bloco)

        questoes_final.append({
            "numero": numero,
            "gabarito": gabarito[numero],
            "enunciado": partes["enunciado"],
            "alternativas": partes["alternativas"],
            "alternativas_completas": partes["completo"],
            "texto_bruto": bloco
        })

    with open(ARQ_AMOSTRA, "w", encoding="utf-8") as f:
        for q in questoes_final[:5]:
            f.write("=" * 100 + "\n")
            f.write(f"QUESTÃO {q['numero']}\n")
            f.write(f"GABARITO: {q['gabarito']}\n")
            f.write(f"ALTERNATIVAS COMPLETAS: {q['alternativas_completas']}\n\n")
            f.write("ENUNCIADO:\n")
            f.write(q["enunciado"] + "\n\n")
            f.write("ALTERNATIVAS:\n")
            if q["alternativas"]:
                for letra, valor in q["alternativas"].items():
                    f.write(f"{letra}) {valor}\n")
            else:
                f.write("Nenhuma alternativa separada.\n")
            f.write("\nTEXTO BRUTO:\n")
            f.write(q["texto_bruto"] + "\n\n")

    with open(ARQ_SAIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(questoes_final, f, ensure_ascii=False, indent=2)

    with open(ARQ_SAIDA_DEBUG, "w", encoding="utf-8") as f:
        json.dump(debug, f, ensure_ascii=False, indent=2)

    completas = [q["numero"] for q in questoes_final if q["alternativas_completas"]]
    incompletas = [q["numero"] for q in questoes_final if not q["alternativas_completas"]]

    with open(ARQ_RELATORIO, "w", encoding="utf-8") as f:
        f.write("RELATÓRIO DE PROCESSAMENTO\n")
        f.write("=" * 60 + "\n")
        f.write(f"PDF prova: {PDF_PROVA.name}\n")
        f.write(f"PDF gabarito: {PDF_GABARITO.name}\n")
        f.write(f"Questões no gabarito: {len(gabarito)}\n")
        f.write(f"Questões encontradas: {len(questoes_final)}\n")
        f.write(f"Questões faltando: {faltando}\n\n")
        f.write(f"Questões com alternativas completas: {completas}\n")
        f.write(f"Questões com alternativas incompletas: {incompletas}\n")

    print("\nPROCESSAMENTO FINALIZADO")
    print(f"Questões no gabarito: {len(gabarito)}")
    print(f"Questões encontradas: {len(questoes_final)}")
    print(f"Questões faltando: {faltando}")
    print(f"Questões com alternativas completas: {len(completas)}")
    print(f"Questões com alternativas incompletas: {len(incompletas)}")
    print("\nArquivos gerados:")
    print(f"- {ARQ_SAIDA_JSON}")
    print(f"- {ARQ_SAIDA_DEBUG}")
    print(f"- {ARQ_RELATORIO}")
    print(f"- {ARQ_AMOSTRA}")


if __name__ == "__main__":
    processar()