import csv
import requests
from bs4 import BeautifulSoup

url = "https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enade/provas-e-gabaritos/2023"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)

print("STATUS:", response.status_code)

if response.status_code != 200:
    print("Erro ao acessar a página de 2023.")
    raise SystemExit

soup = BeautifulSoup(response.text, "html.parser")

pdfs = []

for link in soup.find_all("a"):
    texto = link.get_text(" ", strip=True)
    href = link.get("href")

    if not href:
        continue

    if href.startswith("/"):
        href = "https://www.gov.br" + href

    if ".pdf" in href.lower():
        pdfs.append([texto, href])

with open("output/pdfs_2023.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["texto", "url_pdf"])
    writer.writerows(pdfs)

print("Total de PDFs encontrados:", len(pdfs))
print("Arquivo gerado em: output/pdfs_2023.csv")

for item in pdfs[:20]:
    print(item)