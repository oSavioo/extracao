import re
import unicodedata
from typing import Optional, Tuple

ROMANOS = r"(?:I|II|III|IV|V|VI|VII|VIII|IX|X)"

SUBSTITUICOES_FIXAS = {
    "anti gos": "antigos",
    "multi dimensional": "multidimensional",
    "justi fi cati va": "justificativa",
    "justi fi cativa": "justificativa",
    "confl itos": "conflitos",
    "geopolíti cos": "geopolíticos",
    "políti cas": "políticas",
    "econômi cas": "econômicas",
    "climáti cas": "climáticas",
    "prati camente": "praticamente",
    "desafi o": "desafio",
    "investi mentos": "investimentos",
    "democrati zação": "democratização",
    "conscienti zação": "conscientização",
    "imunizan te": "imunizante",
    "poliomieli te": "poliomielite",
    "hepa ti te": "hepatite",
    "Hepa te A": "Hepatite A",
    "acessoaos": "acesso aos",
    "pelaágua": "pela água",
    "taxacaiu": "taxa caiu",
    "osúltimosanos": "os últimos anos",
    "deidade": "de idade",
    "infanti l": "infantil",
    "gráfi co": "gráfico",
    "gr á fi c o": "gráfico",
    "Arti fi cial": "Artificial",
    "generati va": "generativa",
    "identi fi cação": "identificação",
    "diagnósti co": "diagnóstico",
    "úti l": "útil",
    "substi tuir": "substituir",
    "profi ssões": "profissões",
    "ati vidades": "atividades",
    "repeti ti vas": "repetitivas",
    "esti mula": "estimula",
    "uti lizados": "utilizados",
    "senti am": "sentiam",
    "relati vas": "relativas",
    "ti po": "tipo",
    "Coleti vo": "Coletivo",
    "afi rmações": "afirmações",
    "negati vos": "negativos",
    "coleti vos": "coletivos",
    "refl etem": "refletem",
    "geografi a": "geografia",
    "parti cular": "particular",
    "roti neiros": "rotineiros",
    "forambem": "foram bem",
}

PADROES_FORA_ESCOPO_FORTES = [
    "gráfico", "grafico", "tabela", "figura", "imagem", "imagens",
    "ícone", "ícones", "icones", "charge", "cartum", "mapa",
    "infográfico", "infografico", "fotografia", "ilustração",
    "ilustracao", "esquema", "diagrama", "desenho",
]

PADROES_FORA_ESCOPO_DEPENDENCIA = [
    "o gráfico a seguir mostra",
    "o grafico a seguir mostra",
    "com base no gráfico",
    "com base no grafico",
    "de acordo com o gráfico",
    "de acordo com o grafico",
    "observe a figura",
    "observe o gráfico",
    "observe o grafico",
    "analise a figura",
    "analise o gráfico",
    "analise o grafico",
    "a partir da tabela",
    "a partir do gráfico",
    "a partir do grafico",
    "no gráfico a seguir",
    "no grafico a seguir",
    "na tabela a seguir",
    "na figura a seguir",
    "representado pela cor",
    "barra azul",
    "barra verde",
    "barra amarela",
    "linha vermelha",
    "seta",
    "texto e as imagens apresentados",
    "imagens apresentadas",
    "ícones foram utilizados",
    "icones foram utilizados",
    "situações representadas por tais imagens",
    "situacoes representadas por tais imagens",
    "as respostas relativas a cada tipo",
    "as respostas relativas a cada ti",
]

def _normalizar_basico(texto: str) -> str:
    texto = texto.replace("\r", "\n").replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()

def _remover_rodapes_cabecalhos(texto: str) -> str:
    linhas_ok = []

    for linha in texto.splitlines():
        l = linha.strip()

        if not l:
            linhas_ok.append("")
            continue

        if "VALIDINEP" in l.upper():
            continue

        if re.fullmatch(r"\*\s*\d+\s*\*", l):
            continue

        if re.fullmatch(r"LOGO", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"MAT[ÉE]RIA", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"\d+\s+MAT[ÉE]RIA", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r".*MAT[ÉE]RIA\s+\d*", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"[A-Za-zÀ-ÿ_ ]+\s+\d+\s+\d+\s+MAT[ÉE]RIA", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"[A-Za-zÀ-ÿ_ ]+\s+\d+\s+MAT[ÉE]RIA", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"\*?\s*\d+\s*\*?\s*LOGO(?:\s+MAT[ÉE]RIA)?(?:\s+\d+)?", l, flags=re.IGNORECASE):
            continue

        if re.fullmatch(r"\*?\s*\d+\s*[A-Za-zÀ-ÿ_ ]*", l):
            # pega sobras como "4 Agronomia"
            if "Agronomia" in l or len(l.split()) <= 2:
                continue

        linhas_ok.append(linha)

    texto = "\n".join(linhas_ok)
    return texto.strip()

def _remover_rodape_inline(texto: str) -> str:
    padroes = [
        r"\*\s*\d+\s*\*\s*LOGO(?:\s+MAT[ÉE]RIA)?(?:\s+\d+)?",
        r"\bLOGO(?:\s+MAT[ÉE]RIA)?(?:\s+\d+)?\b",
        r"\bMAT[ÉE]RIA(?:\s+\d+)?\b",
        r"\b\d+\s+Agronomia\b",
        r"\bAgronomia\s+\d+\b",
        r"\b\d+\s+Arquitetura e Urbanismo\b",
        r"\bArquitetura e Urbanismo\s+\d+\b",
        r"\b\d+\s+Biomedicina\b",
        r"\bBiomedicina\s+\d+\b",
        r"\b\d+\s+Enfermagem\b",
        r"\bEnfermagem\s+\d+\b",
        r"\b\d+\s+Engenharia Ambiental\b",
        r"\bEngenharia Ambiental\s+\d+\b",
    ]
    for padrao in padroes:
        texto = re.sub(padrao, " ", texto, flags=re.IGNORECASE)
    return texto

def _remover_blocos_visuais(texto: str) -> str:
    if not texto:
        return texto

    fim = (
        r"considerando\b|com base\b|a partir\b|avalie\b|assinale\b|"
        r"a respeito\b|é correto\b|e correto\b|"
        rf"{ROMANOS}\.\s|1\.\s|2\.\s|3\.\s|4\.\s|5\.\s|$"
    )

    texto = re.sub(
        rf"(?is)foto:\s.*?(?=({fim}|foto:|dispon[ií]vel em:|acesso em:|fonte:))",
        " ",
        texto
    )
    texto = re.sub(
        rf"(?is)dispon[ií]vel em:\s.*?(?=({fim}|acesso em:|fonte:))",
        " ",
        texto
    )
    texto = re.sub(
        rf"(?is)acesso em:\s.*?(?=({fim}))",
        " ",
        texto
    )
    texto = re.sub(
        rf"(?is)fonte:\s.*?(?=({fim}))",
        " ",
        texto
    )

    # sobras típicas de legenda/capção entre o material e o comando
    texto = re.sub(
        r"(?is)\b[a-z]\.\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.]{0,120}\.\s*(?:\d+\.\s*){1,5}(?=\s*Considerando\b)",
        " ",
        texto
    )

    # restos de URL e marcações numéricas isoladas
    texto = re.sub(r"https?\s*:\s*/\s*/\s*\S+", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"https?://\S+", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"www\.\S+", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\b(?:\d+\.\s*){2,}\b", " ", texto)

    return texto

def _aplicar_substituicoes_fixas(texto: str) -> str:
    for errado, certo in SUBSTITUICOES_FIXAS.items():
        texto = texto.replace(errado, certo)
    return texto

def _formatar_blocos_logicos(texto: str) -> str:
    texto = re.sub(r"\bPORQUE\b", "\n\nPORQUE\n\n", texto)

    texto = re.sub(rf"\s*({ROMANOS}\.)\s*", r"\n\1 ", texto)

    texto = re.sub(
        r"\s+(Considerando o texto|Considerando os textos|Considerando as informações|Considerando o estudo apresentado)",
        r"\n\n\1",
        texto
    )

    texto = re.sub(r"\s+(A respeito dessas asserções)", r"\n\n\1", texto)
    texto = re.sub(r"\s+(É correto apenas o que se afirma em)", r"\n\n\1", texto)
    texto = re.sub(r"\s+(É correto o que se afirma em)", r"\n\n\1", texto)
    texto = re.sub(r"\s+(É correto afirmar que)", r"\n\n\1", texto)
    texto = re.sub(r"\s+(avalie as afirmações a seguir)", r"\n\nAvalie as afirmações a seguir", texto, flags=re.IGNORECASE)

    texto = re.sub(r"\.\s*\.", ".", texto)
    texto = re.sub(r"\s{2,}", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()

def limpar_texto_exibicao(texto: str) -> str:
    if not texto:
        return texto

    texto = _normalizar_basico(texto)
    texto = _remover_rodapes_cabecalhos(texto)
    texto = _remover_blocos_visuais(texto)
    texto = _remover_rodape_inline(texto)
    texto = _aplicar_substituicoes_fixas(texto)
    texto = _formatar_blocos_logicos(texto)

    texto = re.sub(r"\s+([,.;:!?])", r"\1", texto)
    texto = re.sub(r"([(\[]) +", r"\1", texto)
    texto = re.sub(r" +([)\]])", r"\1", texto)
    texto = re.sub(r"\n[ ]+", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()

def eh_fora_escopo_visual(bloco_bruto: str) -> bool:
    if not bloco_bruto:
        return False

    t = bloco_bruto.lower()

    tem_visual = any(p in t for p in PADROES_FORA_ESCOPO_FORTES)
    depende_visual = any(p in t for p in PADROES_FORA_ESCOPO_DEPENDENCIA)
    qtd_numeros = len(re.findall(r"\b\d+(?:[.,]\d+)?%?\b", t))

    # bastante rígido para excluir gráficos/tabelas/ícones
    if tem_visual and depende_visual:
        return True

    if tem_visual and qtd_numeros >= 8:
        return True

    return False

def classificar_status_exibicao(status_atual: str, bloco_bruto: str) -> Tuple[str, Optional[str]]:
    if eh_fora_escopo_visual(bloco_bruto):
        return "fora_escopo", "QUESTAO DEPENDE DE ELEMENTO VISUAL"

    return status_atual, None
