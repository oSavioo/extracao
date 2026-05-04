import re
import pdfplumber

caminho = "pdfs/2023_GB_agronomia.pdf"

with pdfplumber.open(caminho) as pdf:
    texto = ""
    for pagina in pdf.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto += texto_pagina + "\n"

padrao = r"QUESTÃO\s+(\d+)\s+([A-E])"
resultados = re.findall(padrao, texto)

print("Total de respostas encontradas:", len(resultados))
print()

for numero, resposta in resultados:
    print(f"Questão {numero} -> {resposta}")