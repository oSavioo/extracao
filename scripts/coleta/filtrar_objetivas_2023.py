import csv

entrada = "output/pdfs_2023.csv"
saida = "output/pdfs_objetivos_2023.csv"

selecionados = []

with open(entrada, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        texto = row["texto"].strip()
        url = row["url_pdf"].strip()
        url_lower = url.lower()

        eh_prova_normal = "/provas_e_gabaritos/" in url_lower and "_pv_" in url_lower
        eh_gabarito_normal = "/provas_e_gabaritos/" in url_lower and "_gb_" in url_lower

        excluir = (
            "ledor" in url_lower
            or "ampliada" in url_lower
            or "super_ampliada" in url_lower
            or "padrao_resposta" in url_lower
        )

        if (eh_prova_normal or eh_gabarito_normal) and not excluir:
            selecionados.append([texto, url])

with open(saida, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["texto", "url_pdf"])
    writer.writerows(selecionados)

print("Total de PDFs úteis:", len(selecionados))
print("Arquivo gerado em:", saida)

for item in selecionados[:30]:
    print(item)