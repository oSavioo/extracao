import re
from extrair_texto_pdf import extrair_texto_pdf

def extrair_gabarito(caminho_pdf: str) -> list[dict]:
    texto = extrair_texto_pdf(caminho_pdf)

    padrao = r"QUESTÃO\s+(\d+)\s+([A-E])"
    encontrados = re.findall(padrao, texto, flags=re.IGNORECASE)

    resultados = []
    for numero, resposta in encontrados:
        resultados.append({
            "numero": int(numero),
            "resposta": resposta.upper()
        })

    return resultados


if __name__ == "__main__":
    caminho = "pdfs/2023_GB_agronomia.pdf"
    gabarito = extrair_gabarito(caminho)

    print("Total encontrado:", len(gabarito))
    for item in gabarito[:10]:
        print(item)