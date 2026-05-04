import argparse
import unicodedata
from pathlib import Path

import requests


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().strip()
    return "_".join(texto.split())


def montar_nome_arquivo(ano: int, tipo: str, curso: str) -> str:
    curso_slug = slugify(curso)
    return f"{ano}_{tipo}_{curso_slug}.pdf"


def baixar_arquivo(url: str, destino: Path):
    headers = {"User-Agent": "Mozilla/5.0"}

    print(f"Baixando: {url}")
    response = requests.get(url, headers=headers, timeout=60)

    if response.status_code != 200:
        raise Exception(f"Erro ao baixar {url} -> status {response.status_code}")

    with open(destino, "wb") as f:
        f.write(response.content)

    print(f"Salvo em: {destino}")
    print(f"Tamanho: {len(response.content)} bytes\n")


def main():
    parser = argparse.ArgumentParser(
        description="Baixa prova e gabarito do ENADE por ano e curso."
    )
    parser.add_argument("--ano", required=True, type=int, help="Ano da prova")
    parser.add_argument("--curso", required=True, type=str, help="Nome do curso")
    parser.add_argument(
        "--tipos",
        nargs="+",
        default=["PV", "GB"],
        choices=["PV", "GB"],
        help="Tipos para baixar: PV, GB ou ambos"
    )
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="Sobrescreve o PDF se ele já existir"
    )

    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    pasta_pdfs = root / "pdfs"
    pasta_pdfs.mkdir(exist_ok=True)

    curso_slug = slugify(args.curso)
    base_url = "https://download.inep.gov.br/enade/provas_e_gabaritos"

    for tipo in args.tipos:
        nome_arquivo = montar_nome_arquivo(args.ano, tipo, args.curso)
        url = f"{base_url}/{nome_arquivo}"
        destino = pasta_pdfs / nome_arquivo

        if destino.exists() and not args.sobrescrever:
            print(f"Arquivo já existe, pulando: {destino}\n")
            continue

        try:
            baixar_arquivo(url, destino)
        except Exception as e:
            print(f"Falha ao baixar {tipo} de {args.curso} ({args.ano})")
            print(f"Motivo: {e}\n")


if __name__ == "__main__":
    main()