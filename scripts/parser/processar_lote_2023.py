import argparse
import sys
from pathlib import Path

from processar_prova_v2 import processar


ROOT = Path(__file__).resolve().parents[2]

CURSOS_ATUAIS_2023 = [
    "agronomia",
    "arquitetura_e_urbanismo",
    "biomedicina",
    "enfermagem",
    "engenharia_ambiental",
    "farmacia",
    "fisioterapia",
    "fonoaudiologia",
    "medicina",
    "medicina_veterinaria",
    "nutricao",
    "odontologia",
]

CURSOS_PENDENTES_2023 = [
    "engenharia_civil",
    "engenharia_de_alimentos",
    "engenharia_da_computacao",
    "engenharia_de_controle_e_automacao",
    "engenharia_de_producao",
    "engenharia_eletrica",
    "engenharia_florestal",
    "engenharia_mecanica",
    "engenharia_quimica",
    "zootecnia",
    "tecnologia_em_agronegocio",
    "tecnologia_em_estetica_e_cosmetico",
    "tecnologia_em_gestao_ambiental",
    "tecnologia_em_gestao_hospitalar",
    "tecnologia_em_radiologia",
    "tecnologia_em_seguranca_do_trabalho",
]


def configurar_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def caminho_pv(pdf_dir: Path, ano: int, curso: str) -> Path:
    return pdf_dir / f"{ano}_PV_{curso}.pdf"


def caminho_gb(pdf_dir: Path, ano: int, curso: str) -> Path:
    return pdf_dir / f"{ano}_GB_{curso}.pdf"


def caminho_saida(output_root: Path, ano: int, curso: str) -> Path:
    return output_root / f"{ano}_{curso}"


def selecionar_cursos(args) -> list[str]:
    if args.todos:
        cursos = CURSOS_ATUAIS_2023 + CURSOS_PENDENTES_2023
    elif args.pendentes:
        cursos = CURSOS_PENDENTES_2023
    elif args.curso:
        cursos = args.curso
    else:
        cursos = CURSOS_ATUAIS_2023

    vistos = set()
    unicos = []
    for curso in cursos:
        curso_norm = curso.strip().lower()
        if curso_norm and curso_norm not in vistos:
            vistos.add(curso_norm)
            unicos.append(curso_norm)
    return unicos


def listar_cursos(cursos: list[str], ano: int, pdf_dir: Path):
    for curso in cursos:
        pv = caminho_pv(pdf_dir, ano, curso)
        gb = caminho_gb(pdf_dir, ano, curso)
        status = "ok" if pv.exists() and gb.exists() else "pdf_pendente"
        print(f"{curso}: {status}")


def processar_curso(curso: str, ano: int, pdf_dir: Path, output_root: Path):
    pv = caminho_pv(pdf_dir, ano, curso)
    gb = caminho_gb(pdf_dir, ano, curso)
    out_dir = caminho_saida(output_root, ano, curso)

    faltando = [str(caminho) for caminho in (pv, gb) if not caminho.exists()]
    if faltando:
        raise FileNotFoundError("PDF ausente: " + ", ".join(faltando))

    print("\n" + "=" * 80)
    print(f"PROCESSANDO {ano} - {curso}")
    print("=" * 80)
    processar(pv, gb, out_dir)


def main():
    configurar_stdout()

    parser = argparse.ArgumentParser(
        description="Processa em lote os cursos ENADE 2023 usando o parser v2."
    )
    parser.add_argument("--ano", type=int, default=2023, help="Ano dos PDFs.")
    parser.add_argument(
        "--curso",
        action="append",
        default=[],
        help="Curso especifico. Pode repetir. Ex: --curso agronomia --curso biomedicina"
    )
    parser.add_argument(
        "--pendentes",
        action="store_true",
        help="Usa a lista de cursos de 2023 ainda pendentes no CSV."
    )
    parser.add_argument(
        "--todos",
        action="store_true",
        help="Usa cursos atuais + cursos pendentes conhecidos."
    )
    parser.add_argument(
        "--listar",
        action="store_true",
        help="Lista os cursos selecionados e se os PDFs existem, sem processar."
    )
    parser.add_argument(
        "--continuar-se-erro",
        action="store_true",
        help="Continua o lote mesmo se um curso falhar."
    )
    parser.add_argument(
        "--pdf-dir",
        type=Path,
        default=ROOT / "pdfs",
        help="Pasta com PDFs PV/GB."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "output" / "v2",
        help="Raiz das saidas v2."
    )
    args = parser.parse_args()

    cursos = selecionar_cursos(args)

    if args.listar:
        listar_cursos(cursos, args.ano, args.pdf_dir)
        return

    erros = []
    for curso in cursos:
        try:
            processar_curso(curso, args.ano, args.pdf_dir, args.output_root)
        except Exception as exc:
            erros.append((curso, exc))
            print(f"\nERRO em {curso}: {exc}")
            if not args.continuar_se_erro:
                raise

    print("\nLOTE FINALIZADO")
    print(f"Cursos tentados: {len(cursos)}")
    print(f"Falhas: {len(erros)}")
    for curso, exc in erros:
        print(f"- {curso}: {exc}")

    if erros:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
