import re

def contar_alternativas(bloco: str) -> int:
    texto = bloco.upper()

    letras_encontradas = set()

    # aceita:
    # A)
    # A.
    # A:
    # A-
    # A texto
    for letra in ["A", "B", "C", "D", "E"]:
        padroes = [
            rf'(^|\n)\s*{letra}[\)\.\:\-]\s+',
            rf'(^|\n)\s*{letra}\s+'
        ]

        for padrao in padroes:
            if re.search(padrao, texto, flags=re.MULTILINE):
                letras_encontradas.add(letra)
                break

    return len(letras_encontradas)


def eh_discursiva(bloco: str) -> bool:
    return "DISCURSIVA" in bloco.upper()


def eh_questionario(bloco: str) -> bool:
    texto = bloco.upper()

    sinais_fortes = [
        "QUESTIONÁRIO DE PERCEPÇÃO DA PROVA",
        "AS QUESTÕES ABAIXO VISAM CONHECER SUA OPINIÃO",
        "AVALIAÇÃO GLOBAL DA PROVA",
        "QUAL O GRAU DE DIFICULDADE DAS QUESTÕES DE FORMAÇÃO GERAL",
        "QUAL O GRAU DE DIFICULDADE DAS QUESTÕES DO COMPONENTE ESPECÍFICO"
    ]

    return any(sinal in texto for sinal in sinais_fortes)


def eh_objetiva(bloco: str) -> bool:
    texto = bloco.upper()

    if eh_discursiva(texto):
        return False

    if eh_questionario(texto):
        return False

    total_alternativas = contar_alternativas(texto)

    return total_alternativas >= 4