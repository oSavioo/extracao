from pathlib import Path
import pdfplumber

def extrair_texto_pdf(caminho_pdf: str) -> str:
    caminho = Path(caminho_pdf)

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")

    texto_total = []

    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                texto_total.append(texto)

    return "\n".join(texto_total)