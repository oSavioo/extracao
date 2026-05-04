import re
import unicodedata
from typing import Optional, Tuple

ROMANOS = r"(?:I|II|III|IV|V|VI|VII|VIII|IX|X)"

SUBSTITUICOES_FIXAS = {
    "PORQUEII.": "PORQUE\n\nII.",
    "PORQUE I.": "PORQUE\n\nI.",
    "PORQUEI.": "PORQUE\n\nI.",
    "justificati va": "justificativa",
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
    "acessoaos": "acesso aos",
    "pelaágua": "pela água",
    "taxacaiu": "taxa caiu",
    "osúltimosanos": "os últimos anos",
    "não ando": "não ando",
    "forambem": "foram bem",
    "deidade": "de idade",
    "corre - se": "corre-se",
    "situa - se": "situa-se",
    "injusti ças": "injustiças",
    "signifi cati va": "significativa",
    "consti tui": "constitui",
    "transmiti das": "transmitidas",
    "afi rma": "afirma",
    "afi rmações": "afirmações",
    "últi mos": "últimos",
    "infanti l": "infantil",
    "gráfi co": "gráfico",
    "arti fi cial": "artificial",
    "generati va": "generativa",
    "identi fi cação": "identificação",
    "diagnósti co": "diagnóstico",
    "úti l": "útil",
    "profi ssões": "profissões",
    "esti mula": "estimula",
    "repeti ti vas": "repetitivas",
    "ati vidades": "atividades",
    "uti lizados": "utilizados",
    "uti lizadas": "utilizadas",
    "ati vamente": "ativamente",
    "refl etem": "refletem",
    "geografi a": "geografia",
    "parti cular": "particular",
    "roti neiros": "rotineiros",
    "gr á fi c o": "gráfico",
    "fi co": "fico",
}
PADROES_FORA_ESCOPO_FORTES = [
    "grafico",
    "graficos",
    "tabela",
    "tabelas",
    "figura",
    "figuras",
    "imagem",
    "imagens",
    "icone",
    "icones",
    "charge",
    "cartum",
    "mapa",
    "infografico",
    "fotografia",
    "ilustracao",
    "esquema",
    "diagrama",
    "desenho",
    "quadro",
    "quadros",
]

PADROES_FORA_ESCOPO_DEPENDENCIA = [
    "o grafico a seguir mostra",
    "o grafico a seguir apresenta",
    "com base no grafico",
    "de acordo com o grafico",
    "observe o grafico",
    "analise o grafico",
    "a partir do grafico",
    "no grafico a seguir",
    "conforme indicado no grafico",
    "texto e no grafico",
    "texto e o grafico apresentados",
    "meta de vacinacao",
    "percentual de vacinacao",
    "imunizante",
    "barra azul",
    "barra verde",
    "barra amarela",
    "linha vermelha",
    "seta",
    "com base na tabela",
    "de acordo com a tabela",
    "observe a tabela",
    "analise a tabela",
    "a partir da tabela",
    "na tabela a seguir",
    "observe a figura",
    "analise a figura",
    "na figura a seguir",
    "texto e as imagens apresentados",
    "imagens apresentadas",
    "os seguintes icones foram utilizados",
    "os seguintes icones foram usados",
    "situacoes representadas por tais imagens",
    "respostas relativas a cada tipo de mobilidade urbana sao apresentadas a seguir",
    "frequento o espaco publico",
    "ando a pe",
    "ando de bicicleta",
    "pego o onibus",
    "ando de metro",
    "ando de trem",
]

PADROES_FORA_ESCOPO_DEPENDENCIA = [
    "o grafico a seguir mostra",
    "o grafico a seguir apresenta",
    "o grafico acima mostra",
    "o grafico acima apresenta",
    "com base no grafico",
    "de acordo com o grafico",
    "observe o grafico",
    "analise o grafico",
    "a partir do grafico",
    "no grafico a seguir",
    "conforme indicado no grafico",
    "texto e o grafico apresentados",
    "texto e no grafico",
    "texto e grafico",
    "meta de vacinacao",
    "percentual de vacinacao",
    "barra azul",
    "barra verde",
    "barra amarela",
    "linha vermelha",
    "seta",
    "na tabela a seguir",
    "a partir da tabela",
    "com base na tabela",
    "de acordo com a tabela",
    "observe a tabela",
    "analise a tabela",
    "na figura a seguir",
    "a figura a seguir",
    "observe a figura",
    "analise a figura",
    "texto e as imagens apresentados",
    "imagens apresentadas",
    "os seguintes icones foram utilizados",
    "os seguintes icones foram usados",
    "situacoes representadas por tais imagens",
    "respostas relativas a cada tipo de mobilidade urbana sao apresentadas a seguir",
    "as respostas relativas a cada tipo",
    "frequento o espaco publico",
    "ando a pe",
    "ando de bicicleta",
    "pego o onibus",
    "ando de metro",
    "ando de trem",
]

def _normalizar_basico(texto: str) -> str:
    texto = texto.replace("\r", "\n").replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()

def _normalizar_para_detecao(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
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
    texto = re.sub(r"\b(I|II|III|IV|V)\s+e\s*\n\s*(I|II|III|IV|V)\.", r"\1 e \2.", texto)
    texto = re.sub(r"\b(I|II|III|IV|V),\s*\n\s*(I|II|III|IV|V)\.", r"\1, \2.", texto)
    texto = re.sub(r"\bPORQUE\s*\n*\s*II\.", "PORQUE\n\nII.", texto)
    texto = re.sub(r"\bPORQUEII\.", "PORQUE\n\nII.", texto)
    texto = re.sub(r"\s{2,}", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()

def eh_fora_escopo_visual(bloco_bruto: str) -> bool:
    if not bloco_bruto:
        return False

    t = _normalizar_para_detecao(bloco_bruto)

    tem_visual = any(p in t for p in PADROES_FORA_ESCOPO_FORTES)
    tem_dependencia = any(p in t for p in PADROES_FORA_ESCOPO_DEPENDENCIA)

    qtd_percentuais = len(re.findall(r"\b\d+(?:[.,]\d+)?%\b", t))
    qtd_numeros = len(re.findall(r"\b\d+(?:[.,]\d+)?\b", t))

    # Caso clássico: questão cita gráfico/tabela/figura e depende dela
    if tem_visual and tem_dependencia:
        return True

    # Questão numérica de gráfico/tabela
    if tem_visual and ("grafico" in t or "tabela" in t) and (qtd_percentuais >= 3 or qtd_numeros >= 12):
        return True

    # Questão de ícones / percepções / modais urbanos
    blocos_textuais_visuais = [
        "atenta",
        "desconfortavel",
        "livre",
        "apertada",
        "em alerta",
        "observada",
        "um pouco mais segura",
        "ansiosa",
        "pessima",
        "cansada",
        "insegura",
        "desconfiada",
        "em panico",
        "passo correndo",
    ]

    qtd_blocos = sum(1 for p in blocos_textuais_visuais if p in t)

    if ("icone" in t or "icones" in t or "imagem" in t or "imagens" in t) and qtd_blocos >= 4:
        return True

    modais = [
        "ando a pe",
        "ando de bicicleta",
        "pego o onibus",
        "ando de metro",
        "ando de trem",
        "frequento o espaco publico",
    ]

    qtd_modais = sum(1 for p in modais if p in t)

    if qtd_modais >= 4 and ("imagem" in t or "icones" in t or "respostas relativas" in t):
        return True

    return False

def classificar_status_exibicao(status_atual: str, bloco_bruto: str):
    if eh_fora_escopo_visual(bloco_bruto):
        return "fora_escopo", "QUESTAO DEPENDE DE ELEMENTO VISUAL"

    return status_atual, None
