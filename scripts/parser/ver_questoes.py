import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARQUIVO_PADRAO = ROOT / "output" / "v2" / "2023_agronomia" / "2023_pv_agronomia_questoes.json"
LETRAS_VALIDAS = ("A", "B", "C", "D", "E")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def carregar_questoes(caminho: Path):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def filtrar_questoes(questoes, status: str, inicio: int | None, fim: int | None):
    selecionadas = []

    for q in questoes:
        numero = q["numero"]
        q_status = (q.get("status") or "").lower()

        if status != "todos" and q_status != status:
            continue

        if inicio is not None and numero < inicio:
            continue

        if fim is not None and numero > fim:
            continue

        selecionadas.append(q)

    return selecionadas


def obter_alternativas_esperadas(q):
    esperadas = q.get("alternativas_esperadas") or []
    letras = [letra for letra in esperadas if letra in LETRAS_VALIDAS]
    return letras or list(LETRAS_VALIDAS)


def imprimir_questao(q):
    print("=" * 120)
    print(f"QUESTAO: {q['numero']}")
    print(f"GABARITO: {q.get('gabarito')}")
    print(f"STATUS: {q.get('status')}")

    if q.get("observacao"):
        print(f"OBSERVACAO: {q.get('observacao')}")

    print()
    print("ENUNCIADO:\n")
    print(q.get("enunciado") or "")

    alternativas = q.get("alternativas") or {}
    for letra in obter_alternativas_esperadas(q):
        print(f"\n{letra}:\n")
        print(alternativas.get(letra, ""))

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Visualiza questoes extraidas. Por padrao mostra somente questoes jogaveis."
    )
    parser.add_argument(
        "arquivo",
        nargs="?",
        type=Path,
        default=ARQUIVO_PADRAO,
        help="Arquivo *_questoes.json a visualizar."
    )
    parser.add_argument(
        "--status",
        choices=["completa", "fora_escopo", "incompleta", "nao_encontrada", "todos"],
        default="completa",
        help="Status a exibir. Padrao: completa."
    )
    parser.add_argument("--inicio", type=int, help="Numero inicial da questao.")
    parser.add_argument("--fim", type=int, help="Numero final da questao.")
    parser.add_argument(
        "--limite",
        type=int,
        default=10,
        help="Quantidade maxima de questoes exibidas. Use 0 para exibir todas."
    )
    args = parser.parse_args()

    questoes = carregar_questoes(args.arquivo)
    selecionadas = filtrar_questoes(questoes, args.status, args.inicio, args.fim)

    if args.limite > 0:
        selecionadas = selecionadas[:args.limite]

    print(f"Arquivo: {args.arquivo}")
    print(f"Filtro status: {args.status}")
    print(f"Questoes exibidas: {len(selecionadas)}")
    print()

    for q in selecionadas:
        imprimir_questao(q)


if __name__ == "__main__":
    main()
