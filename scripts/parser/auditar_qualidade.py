import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

from pos_processar_exibicao import eh_fora_escopo_visual


ROOT = Path(__file__).resolve().parents[2]
STATUS_OK = "completa"
LETRAS_VALIDAS = ("A", "B", "C", "D", "E")


def configurar_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower()
    return re.sub(r"\s+", " ", texto).strip()


def carregar_json(caminho: Path):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def obter_alternativas_esperadas(questao: dict) -> list[str]:
    esperadas = questao.get("alternativas_esperadas") or []
    letras = [letra for letra in esperadas if letra in LETRAS_VALIDAS]
    return letras or list(LETRAS_VALIDAS)


def iter_arquivos(output_root: Path, ano: int | None, cursos: set[str] | None):
    if ano is None:
        candidatos = sorted(output_root.glob("*/*_questoes.json"))
    else:
        candidatos = sorted(output_root.glob(f"{ano}_*/*_questoes.json"))

    for caminho in candidatos:
        nome_pasta = caminho.parent.name
        curso = re.sub(r"^\d{4}_", "", nome_pasta)
        if cursos and curso not in cursos:
            continue
        yield caminho


def detectar_problemas_fortes(questao: dict):
    enunciado = questao.get("enunciado") or ""
    alternativas = questao.get("alternativas") or {}
    letras_esperadas = obter_alternativas_esperadas(questao)
    texto = " ".join(
        [enunciado] + [alternativas.get(letra, "") or "" for letra in letras_esperadas]
    )
    texto_norm = normalizar(texto)

    problemas = []

    if len(enunciado.strip()) < 80:
        problemas.append("enunciado_curto")

    for letra in letras_esperadas:
        if not (alternativas.get(letra) or "").strip():
            problemas.append(f"alternativa_{letra}_vazia")

    gabarito = questao.get("gabarito")
    if gabarito in LETRAS_VALIDAS and gabarito not in letras_esperadas:
        problemas.append("gabarito_fora_das_alternativas")

    padroes = [
        ("seguinte_figura", r"\bseguinte figura\b"),
        ("figura_numerada", r"\bfigura\s+\d+\b"),
        ("rodape_validinep", r"validinep|validin3p"),
        ("pos_prova", r"avalia.{0,30}global.{0,20}prova|question.{0,30}percepc.{0,30}prova"),
        ("url_solta", r"https?\s*:|www\."),
    ]

    for nome, padrao in padroes:
        if re.search(padrao, texto_norm):
            problemas.append(nome)

    if "\ufffd" in texto:
        problemas.append("caractere_invalido")

    return problemas


def auditar_arquivo(caminho: Path):
    questoes = carregar_json(caminho)
    contagem = {}
    problemas = []
    inconsistencias = []

    for questao in questoes:
        status = questao.get("status")
        numero = questao.get("numero")
        contagem[status] = contagem.get(status, 0) + 1

        if status == STATUS_OK:
            fortes = detectar_problemas_fortes(questao)
            if fortes:
                problemas.append((numero, fortes))

            texto_bruto = questao.get("texto_bruto") or ""
            if eh_fora_escopo_visual(texto_bruto):
                inconsistencias.append((numero, "detector_marcaria_fora_escopo"))

    return {
        "arquivo": caminho,
        "contagem": contagem,
        "problemas": problemas,
        "inconsistencias": inconsistencias,
    }


def main():
    configurar_stdout()

    parser = argparse.ArgumentParser(
        description="Audita os JSONs do parser v2 para achar problemas fortes nas questoes completas."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "output" / "v2",
        help="Raiz do output v2."
    )
    parser.add_argument("--ano", type=int, default=2023, help="Ano a auditar. Use 0 para todos.")
    parser.add_argument(
        "--curso",
        action="append",
        default=[],
        help="Curso especifico para auditar. Pode repetir. Ex: --curso agronomia --curso biomedicina"
    )
    parser.add_argument(
        "--falhar-se-problema",
        action="store_true",
        help="Retorna codigo 1 se encontrar problema forte ou inconsistencia."
    )
    args = parser.parse_args()

    ano = None if args.ano == 0 else args.ano
    cursos = {c.strip().lower() for c in args.curso if c.strip()} or None
    arquivos = list(iter_arquivos(args.output_root, ano, cursos))

    if not arquivos:
        print("Nenhum arquivo *_questoes.json encontrado para os filtros informados.")
        raise SystemExit(1)

    resultados = [auditar_arquivo(caminho) for caminho in arquivos]

    total_problemas = 0
    total_inconsistencias = 0
    totais_status = {}

    print("RESUMO")
    for resultado in resultados:
        nome = resultado["arquivo"].parent.name
        print(f"{nome}: {resultado['contagem']}")
        for status, qtd in resultado["contagem"].items():
            totais_status[status] = totais_status.get(status, 0) + qtd

    print(f"\nTOTAL: {totais_status}")

    print("\nPROBLEMAS FORTES")
    for resultado in resultados:
        nome = resultado["arquivo"].parent.name
        for numero, problemas in resultado["problemas"]:
            total_problemas += 1
            print(f"{nome} Q{numero}: {', '.join(problemas)}")

    if total_problemas == 0:
        print("Nenhum problema forte encontrado nas questoes completas.")

    print("\nINCONSISTENCIAS COM DETECTOR ATUAL")
    for resultado in resultados:
        nome = resultado["arquivo"].parent.name
        for numero, motivo in resultado["inconsistencias"]:
            total_inconsistencias += 1
            print(f"{nome} Q{numero}: {motivo}")

    if total_inconsistencias == 0:
        print("Nenhuma inconsistencia encontrada.")

    if args.falhar_se_problema and (total_problemas or total_inconsistencias):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
