import csv
import re
from collections import defaultdict

entrada = "output/pdfs_objetivos_2023.csv"

cursos = defaultdict(set)

padrao = re.compile(r'2023_(PV|GB)_(.+)\.pdf$', re.IGNORECASE)

with open(entrada, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        url = row["url_pdf"].strip()
        match = padrao.search(url)

        if match:
            tipo = match.group(1).upper()
            curso = match.group(2).lower()
            cursos[curso].add(tipo)

print("Validação dos pares:\n")

faltando = False

for curso in sorted(cursos.keys()):
    tipos = cursos[curso]

    if "PV" in tipos and "GB" in tipos:
        print(f"[OK] {curso} -> tem PV e GB")
    else:
        faltando = True
        print(f"[ERRO] {curso} -> tipos encontrados: {tipos}")

if not faltando:
    print("\nTodos os cursos possuem par completo.")