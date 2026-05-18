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
    "insufi cientes": "insuficientes",
    "legislati vas": "legislativas",
    "políti ca": "política",
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
    "noti fi caÃ§Ãµes": "notificaÃ§Ãµes",
    "fi xaÃ§Ã£o": "fixaÃ§Ã£o",
    "justi fi cati": "justificati",
    "ressignifi caÃ§Ã£o": "ressignificaÃ§Ã£o",
    "artÃ­ sti ca": "artÃ­stica",
    "refl exÃ£o": "reflexÃ£o",
    "noti fi caÃ§Ãµes": "notificaÃ§Ãµes",
    "justificati va": "justificativa",
    "substi tuir": "substituir",
    "noti fi cações": "notificações",
    "fi xação": "fixação",
    "ressignifi cação": "ressignificação",
    "artí sti ca": "artística",
    "refl exão": "reflexão",
    "disrupti va": "disruptiva",
    "drasti camente": "drasticamente",
    "maléfi cas": "maléficas",
    "éti cas": "éticas",
    "parti cipação": "participação",
    "classifi cadas": "classificadas",
    "insti tucional": "institucional",
    "desati vação": "desativação",
    "aplicati vos": "aplicativos",
    "profi ssional": "profissional",
    "recreati vo": "recreativo",
    "ti nha": "tinha",
    "ti po": "tipo",
    "gati lhos": "gatilhos",
    "ti ros": "tiros",
    "menti ra": "mentira",
    "identi dade": "identidade",
    "personifi ca": "personifica",
    "Justi ça": "Justiça",
    "fi lha": "filha",
    "fi lmes": "filmes",
    "Typografi a": "Typografia",
    "Mesti ço": "Mestiço",
    "Porti nari": "Portinari",
    "arti sta": "artista",
    "identi dade": "identidade",
    "ressignifi cação": "ressignificação",
    "A parti r": "A partir",
    "defi nição": "definição",
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
    "fluxograma",
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

PADROES_FORA_ESCOPO_DEPENDENCIA.extend([
    "conforme apresentado no grafico",
    "texto e o grafico",
    "informacoes apresentadas no texto e no grafico",
    "informacoes apresentadas no grafico",
    "apresentadas no grafico",
    "tabela a seguir",
    "resultados apresentados na tabela",
    "dados apresentados na tabela",
    "informacoes apresentadas na tabela",
    "apresentado na tabela",
    "apresentados na tabela",
    "figura a seguir",
    "figura acima",
    "com base na figura",
    "com base no texto e na figura",
    "texto e na figura",
    "texto e figura",
    "conforme ilustrado na figura",
    "ilustrado na figura",
    "ilustra este cenario",
    "na figura do mapa",
    "mapa de doses",
    "mapa de aplicacao",
    "mapa a seguir",
    "com base no mapa",
    "de acordo com o mapa",
    "observe o mapa",
    "analise o mapa",
    "no quadro a seguir",
    "quadro a seguir",
    "com base no quadro",
    "de acordo com o quadro",
    "texto e imagens apresentados",
    "imagem apresentada",
    "seguinte figura",
    "figura 1",
    "figura 2",
    "figura 3",
    "visualiza as estruturas a seguir",
    "visualizaram as estruturas a seguir",
    "estruturas a seguir",
    "observe, a seguir, os resultados",
    "observe a seguir os resultados",
    "resultados da tipagem sanguinea",
    "presenca de aglutinacao",
    "ausencia de aglutinacao",
    "anti-a",
    "anti-b",
    "anti-d",
    "tipos de secadores",
    "fluxo cruzado",
    "fluxo concorrente",
    "fluxo contracorrente",
    "fluxo misto",
    "produto ar de secagem ar de exaustao",
    "equacao booleana a seguir",
    "ilustra a equacao booleana",
    "resultado logico da equacao original fornecida",
    "portas logicas originais",
])

NOMES_CURSOS_RODAPE = [
    r"Agronomia",
    r"Arquitetura e Urbanismo",
    r"Biomedicina",
    r"Enfermagem",
    r"Engenharia Ambiental",
    r"Engenharia Civil",
    r"Engenharia de Alimentos",
    r"Engenharia da Computa\S+",
    r"Engenharia de Controle e Automa\S+o",
    r"Engenharia de Produ\S+o",
    r"Engenharia El\S+trica",
    r"Engenharia Florestal",
    r"Engenharia Mec\S+nica",
    r"Engenharia Qu\S+mica",
    r"Farm\S+cia",
    r"Fisioterapia",
    r"Fonoaudiologia",
    r"Medicina",
    r"Medicina Veterin\S+ria",
    r"Nutri\S+o",
    r"Odontologia",
    r"Tecnologia em Agroneg\S+cio",
    r"Tecnologia em Est\S+tica e Cosm\S+tica",
    r"Tecnologia em Gest\S+o Ambiental",
    r"Tecnologia em Gest\S+o Hospitalar",
    r"Tecnologia em Radiologia",
    r"Tecnologia em Seguran\S+a do Trabalho",
    r"Zootecnia",
]

CURSOS_RODAPE_RE = r"(?:" + "|".join(NOMES_CURSOS_RODAPE) + r")"

def _normalizar_basico(texto: str) -> str:
    texto = texto.replace("\r", "\n").replace("\xa0", " ")
    texto = texto.replace("\ufffd", "")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()

def _normalizar_para_detecao(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

def _normalizar_quebras_visuais(texto: str) -> str:
    compactadores = {
        r"\bg\s*r\s*a\s*f\s*i\s*c\s*o(?:s|\s+s)?\b": "grafico",
        r"\bt\s*a\s*b\s*e\s*l\s*a(?:s|\s+s)?\b": "tabela",
        r"\bf\s*i\s*g\s*u\s*r\s*a(?:s|\s+s)?\b": "figura",
        r"\bi\s*m\s*a\s*g\s*e\s*n\s*s\b": "imagens",
        r"\bi\s*m\s*a\s*g\s*e\s*m\b": "imagem",
        r"\bi\s*c\s*o\s*n\s*e(?:s|\s+s)?\b": "icone",
        r"\bi\s*n\s*f\s*o\s*g\s*r\s*a\s*f\s*i\s*c\s*o\b": "infografico",
        r"\bd\s*i\s*a\s*g\s*r\s*a\s*m\s*a\b": "diagrama",
        r"\bq\s*u\s*a\s*d\s*r\s*o(?:s|\s+s)?\b": "quadro",
    }

    for padrao, substituto in compactadores.items():
        texto = re.sub(padrao, substituto, texto)

    return texto

def _contem_termo(texto: str, termo: str) -> bool:
    if " " in termo:
        return termo in texto

    return re.search(rf"\b{re.escape(termo)}\b", texto) is not None

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

        if re.fullmatch(
            rf"\*?\s*(?:\d+\s+)?{CURSOS_RODAPE_RE}(?:\s+\d+)?(?:\s+MAT[ÉE]RIA)?",
            l,
            flags=re.IGNORECASE
        ):
            continue

        if re.fullmatch(r"\*?\s*\d+\s*[A-Za-zÀ-ÿ_ ]*", l):
            # pega sobras como "4 Agronomia"
            if re.search(CURSOS_RODAPE_RE, l, flags=re.IGNORECASE) or len(l.split()) <= 2:
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
    for nome_curso in NOMES_CURSOS_RODAPE:
        padroes.append(rf"(?m)(?:^|\s)\d+\s+{nome_curso}(?=\s*$)")
        padroes.append(rf"(?m)(?:^|\s){nome_curso}\s+\d+(?=\s*$)")

    for padrao in padroes:
        texto = re.sub(padrao, " ", texto, flags=re.IGNORECASE)
    return texto

def _remover_secoes_pos_prova(texto: str) -> str:
    padroes = [
        r"(?is)\bAVALIA.{0,20}?GLOBAL\s+DA\s+P\s*ROVA\b.*$",
        r"(?is)\bQUESTION.{0,20}?RIO\s+DE\s+PERCEP.{0,20}?O\s+SOBRE\s+A\s+PROVA\b.*$",
        r"(?is)\bIMPRESS.{0,20}?O\s+SOBRE\s+A\s+PROVA\b.*$",
    ]

    for padrao in padroes:
        texto = re.sub(padrao, " ", texto)

    return texto

def _remover_blocos_visuais(texto: str) -> str:
    if not texto:
        return texto

    # Remove referencias sem engolir textos posteriores, como TEXTO 2.
    texto = re.sub(
        r"(?is)dispon[ií]vel em:[\s\S]{0,600}?acesso em:?\s*\d{1,2}(?:\s+de)?\s+[a-zç.]+\s+\d{4}\s*(?:\([^)]*\))?\.?",
        " ",
        texto
    )
    texto = re.sub(
        r"(?is)dispon[ií]vel em:\s*acesso em:?\s*\d{1,2}(?:\s+de)?\s+[a-zç.]+\s+\d{4}\s*(?:\([^)]*\))?\.?",
        " ",
        texto
    )
    texto = re.sub(
        r"(?is)\bacesso em:\s*\d{1,2}\s+[a-zç.]+\s+\d{4}\s*(?:\([^)]*\))?\.?",
        " ",
        texto
    )
    texto = re.sub(
        r"(?is)\bacesso em:?\s*\d{1,2}(?:\s+de)?\s+[a-zç.]+\s+\d{4}\s*(?:\([^)]*\))?\.?",
        " ",
        texto
    )
    texto = re.sub(
        r"(?im)^\s*dispon[iÃ­]vel em:\s.*(?:\n\s*(?!TEXTO\b|Considerando\b|Com base\b|A partir\b|Avalie\b|Assinale\b|[IVX]+\.).*){0,2}",
        " ",
        texto
    )
    texto = re.sub(r"(?im)^\s*acesso em:\s.*$", " ", texto)
    texto = re.sub(
        r"(?is)\bdispon[ií]vel em:\s*(?:acesso(?:\s+em)?\s*:?\s*\d{1,2}(?:\s+de)?\s+[a-zç.]+\.?\s*\d{4}\s*)?(?:\([^)]*\)\.?)?\s*(?=(?:TEXTO\s+\d+|Considerando|Com rela[cç][aã]o|Acerca|A partir|Avalie|Assinale)\b)",
        " ",
        texto
    )
    texto = re.sub(
        r"(?is)\bacesso(?:\s+em)?\s*:?\s*\d{1,2}(?:\s+de)?\s+[a-zç.]+\.?\s*\d{4}\s*(?:\([^)]*\)\.?)?\s*(?=(?:TEXTO\s+\d+|Considerando|Com rela[cç][aã]o|Acerca|A partir|Avalie|Assinale)\b)",
        " ",
        texto
    )

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
        rf"(?is)^\b$DISPONIVEL_JA_REMOVIDO\s.*?(?=({fim}|acesso em:|fonte:))",
        " ",
        texto
    )
    texto = re.sub(
        rf"(?is)^\b$ACESSO_JA_REMOVIDO\s.*?(?=({fim}))",
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
        texto = re.sub(re.escape(errado), certo, texto, flags=re.IGNORECASE)
    texto = re.sub(r"justificati\s+va", "justificativa", texto, flags=re.IGNORECASE)
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
    texto = _remover_secoes_pos_prova(texto)
    texto = _remover_blocos_visuais(texto)
    texto = _remover_rodape_inline(texto)
    texto = _remover_secoes_pos_prova(texto)
    texto = _aplicar_substituicoes_fixas(texto)
    texto = _remover_secoes_pos_prova(texto)
    texto = _formatar_blocos_logicos(texto)
    texto = re.sub(r"(?i)\bdispon.{0,3}vel em:\s*(?:\([^)]*\)\.?)?", " ", texto)
    texto = re.sub(
        r"(?i)\bacesso(?:\s+em)?\s*:?\s*\d{1,2}(?:\s+de)?\s+[a-zç.]+\.?\s*\d{4}\s*(?:\([^)]*\)\.?)?",
        " ",
        texto
    )

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

    t = _normalizar_quebras_visuais(_normalizar_para_detecao(bloco_bruto))
    t = re.sub(r"\b(?:imagem|imagens)\s+radiograficas?\b", "exame radiografico", t)

    tem_visual = any(_contem_termo(t, p) for p in PADROES_FORA_ESCOPO_FORTES)
    tem_dependencia = any(p in t for p in PADROES_FORA_ESCOPO_DEPENDENCIA)

    qtd_percentuais = len(re.findall(r"\b\d+(?:[.,]\d+)?%\b", t))
    qtd_numeros = len(re.findall(r"\b\d+(?:[.,]\d+)?\b", t))
    qtd_comparadores = len(re.findall(r"(?:<|>|<=|>=)\s*\d+", t))
    qtd_razoes = len(re.findall(r"\b\d+\s*:\s*\d+", t))
    qtd_linhas = len([linha for linha in bloco_bruto.splitlines() if linha.strip()])

    dependencia_regex = [
        r"\b(?:com base|a partir|de acordo|considerando|conforme|observe|analise)\b.{0,90}\b(?:grafico|tabela|figura|imagem|imagens|mapa|quadro|diagrama)\b",
        r"\b(?:grafico|tabela|figura|imagem|imagens|mapa|quadro|diagrama)\b.{0,30}\b(?:a seguir|acima|abaixo)\b",
        r"\b(?:grafico|tabela|figura|imagem|imagens|mapa|quadro|diagrama)\b.{0,70}\b(?:apresentad[ao]s?|ilustrad[ao]s?|mostra|apresenta|indica)\b",
        r"\b(?:resultados|dados|informacoes|respostas)\b.{0,80}\b(?:apresentad[ao]s?|representad[ao]s?)\b.{0,50}\b(?:tabela|grafico|figura|imagem|imagens|mapa|quadro)\b",
        r"\b(?:observe|analise|visualize|visualiza|visualizam|visualizaram)\b.{0,80}\b(?:a seguir|abaixo|acima)\b",
        r"\b(?:estruturas|resultados|amostras|laminas?|micrografias?)\b.{0,80}\b(?:a seguir|visualizad[ao]s?|apresentad[ao]s?)\b",
    ]

    if any(re.search(padrao, t) for padrao in dependencia_regex):
        return True

    if (
        "equacao booleana a seguir" in t
        and (
            "ilustra a equacao booleana" in t
            or "portas logicas originais" in t
            or "resultado logico da equacao original fornecida" in t
        )
    ):
        return True

    if "numero de froude" in t and "numero de reynolds" in t:
        return True

    if (
        "pseudocodigo apresentado a seguir" in t
        and (
            "variavel real num" in t
            or "variavel inteiro" in t
            or "para i de 1 ate" in t
        )
    ):
        return True

    if (
        "comportamento dinamico do nivel" in t
        and "tempo (s)" in t
        and "nivel do tanque" in t
    ):
        return True

    if (
        "modelo do reator" in t
        and "lei da conservacao da massa" in t
        and "lei de fick" in t
    ):
        return True

    if "infografico a seguir" in t or "informacoes do infografico" in t:
        return True

    if "mapas a seguir" in t or "interpretacao dos mapas" in t:
        return True

    if (
        "esquema a seguir representa" in t
        or "esquema a seguir mostra" in t
        or "esquema apresentado a seguir" in t
        or "fluxograma a seguir representa" in t
        or "referencia da figura" in t
        or "apresentado na figura" in t
    ):
        return True

    if "folha como a representada a seguir" in t:
        return True

    if "vetores de tamanho dinamico" in t and "qq(" in t:
        return True

    if "torre de absorcao reativa" in t and "balanco de massa" in t and "d c" in t and "kcn" in t:
        return True

    tabela_extraida_sem_rotulo = [
        "resultado referencia",
        "resultado referencias",
        "resultados descritos a seguir",
        "resultados apresentados a seguir",
        "dados descritos a seguir",
        "dados apresentados a seguir",
        "exames laboratoriais resultados",
        "valores referenciais",
        "categoria referencial",
        "categoria de risco",
        "parametro resultado valor de referencia",
        "resultado valor de referencia",
        "aspecto amarelo",
        "citometria",
        "citologia",
        "bacterioscopia",
        "hemograma exame de urina",
        "com jejum",
        "sem jejum",
    ]

    qtd_indicios_tabela = sum(1 for p in tabela_extraida_sem_rotulo if p in t)
    unidades_tabela = len(re.findall(r"\b(?:mg/dl|g/dl|mmhg|bpm|irpm|kg|ml|cm|mmol/l)\b", t))

    if qtd_indicios_tabela >= 2 and (qtd_linhas >= 20 or qtd_numeros >= 12 or qtd_comparadores >= 4):
        return True

    if "resultado referencia" in t and (qtd_linhas >= 18 or qtd_numeros >= 12 or qtd_comparadores >= 4):
        return True

    if "valor de referencia" in t and (qtd_linhas >= 20 or qtd_numeros >= 18):
        return True

    if unidades_tabela >= 6 and (qtd_linhas >= 20 or qtd_comparadores >= 4):
        return True

    if "prevalencia" in t and qtd_razoes >= 4:
        return True

    if "avaliacao microscopica" in t and ("lamina" in t or "laminula" in t) and "visualiza" in t:
        return True

    if "tipagem sanguinea" in t and ("observe" in t or "resultados apresentados" in t):
        return True

    if "seguinte figura" in t:
        return True

    if re.search(r"\bfigura\s+\d+\b", t):
        return True

    if "tipos de secadores" in t and "fluxo" in t and ("ar de secagem" in t or "ar de exaustao" in t):
        return True

    if qtd_linhas >= 25 and len(re.findall(r"\bfluxo\b", t)) >= 8 and ("a)" in t or "b)" in t):
        return True

    termos_visuais_arquitetura = [
        "planta do pavimento",
        "planta de cobertura",
        "fachada norte",
        "fachada frontal",
        "vista superior",
        "vista leste",
        "vista oeste",
        "implantacao",
        "quadro poliesportiva",
        "acesso em: 18 ago. 2023",
        "archdaily",
        "vitruvius",
        "tecverde",
        "gazetadopovo",
        "opovo.com.br",
        "wribrasil",
        "image_view_fullscreen",
        "jpg",
        "exemplo de intervencoes",
        "ruas completas",
    ]

    comandos_visuais_arquitetura = [
        "obra apresentada",
        "projeto apresentado",
        "edificacao apresentada",
        "componentes da edificacao apresentada",
        "sistema adotado no projeto",
        "desenho de uma planta",
        "indicacao da vista",
        "mencionada elevacao",
        "forma do lugar",
        "paisagem urbana",
        "composicao da fachada",
        "desenho viario",
    ]

    qtd_termos_arq = sum(1 for p in termos_visuais_arquitetura if p in t)
    qtd_comandos_arq = sum(1 for p in comandos_visuais_arquitetura if p in t)

    if "arquitetura e urbanismo" in t and (qtd_termos_arq >= 1 or qtd_comandos_arq >= 1):
        return True

    if qtd_comandos_arq >= 1 and ("fachada" in t or "planta" in t or "vista" in t or "projeto" in t):
        return True

    # Provas de arquitetura podem trazer pranchas/fotos de obras apenas como legendas.
    if t.count("arquiteto:") >= 2:
        return True

    # Caso clássico: questão cita gráfico/tabela/figura e depende dela
    if tem_visual and tem_dependencia:
        return True

    tem_grafico = _contem_termo(t, "grafico")
    tem_tabela = _contem_termo(t, "tabela")
    tem_figura = _contem_termo(t, "figura")
    tem_mapa = _contem_termo(t, "mapa")
    tem_quadro = _contem_termo(t, "quadro")
    tem_imagem = _contem_termo(t, "imagem")
    tem_imagens = _contem_termo(t, "imagens")
    tem_icone = _contem_termo(t, "icone")
    tem_icones = _contem_termo(t, "icones")

    # Questão numérica de gráfico/tabela
    if tem_visual and (tem_grafico or tem_tabela) and (qtd_percentuais >= 3 or qtd_numeros >= 12):
        return True

    # Tabelas extraidas como texto deixam muitas linhas e muitos numeros.
    if (tem_tabela or tem_quadro) and qtd_linhas >= 30 and qtd_numeros >= 20:
        return True

    # Figuras/mapas/graficos costumam deixar percentuais e rotulos visuais no texto extraido.
    if (tem_figura or tem_mapa or tem_grafico) and (qtd_percentuais >= 4 or qtd_numeros >= 18):
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

    if (tem_icone or tem_icones or tem_imagem or tem_imagens) and qtd_blocos >= 4:
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

    if qtd_modais >= 4 and (tem_imagem or tem_icones or "respostas relativas" in t):
        return True

    return False

def classificar_status_exibicao(status_atual: str, bloco_bruto: str):
    if eh_fora_escopo_visual(bloco_bruto):
        return "fora_escopo", "QUESTAO DEPENDE DE ELEMENTO VISUAL"

    return status_atual, None
