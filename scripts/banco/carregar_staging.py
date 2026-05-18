import json
import re
import argparse
import sys
from pathlib import Path

import psycopg2

PARSER_DIR = Path(__file__).resolve().parents[1] / "parser"
sys.path.insert(0, str(PARSER_DIR))

from escopo_manual_2023 import eh_fora_escopo_manual_2023


# ============================================
# CONFIGURAÇÕES
# ============================================
VERSAO_PARSER = "V2"

NOMES_CURSOS = {
    "agronomia": "Agronomia",
    "arquitetura_e_urbanismo": "Arquitetura e Urbanismo",
    "biomedicina": "Biomedicina",
    "enfermagem": "Enfermagem",
    "engenharia_ambiental": "Engenharia Ambiental",
    "engenharia_civil": "Engenharia Civil",
    "engenharia_da_computacao": "Engenharia da Computação",
    "engenharia_de_alimentos": "Engenharia de Alimentos",
    "engenharia_de_controle_e_automacao": "Engenharia de Controle e Automação",
    "engenharia_de_producao": "Engenharia de Produção",
    "engenharia_eletrica": "Engenharia Elétrica",
    "engenharia_florestal": "Engenharia Florestal",
    "engenharia_mecanica": "Engenharia Mecânica",
    "engenharia_quimica": "Engenharia Química",
    "farmacia": "Farmácia",
    "fisioterapia": "Fisioterapia",
    "fonoaudiologia": "Fonoaudiologia",
    "medicina": "Medicina",
    "medicina_veterinaria": "Medicina Veterinária",
    "nutricao": "Nutrição",
    "odontologia": "Odontologia",
    "tecnologia_em_agronegocio": "Tecnologia em Agronegócio",
    "tecnologia_em_estetica_e_cosmetico": "Tecnologia em Estética e Cosmética",
    "tecnologia_em_gestao_ambiental": "Tecnologia em Gestão Ambiental",
    "tecnologia_em_gestao_hospitalar": "Tecnologia em Gestão Hospitalar",
    "tecnologia_em_radiologia": "Tecnologia em Radiologia",
    "tecnologia_em_seguranca_do_trabalho": "Tecnologia em Segurança do Trabalho",
    "zootecnia": "Zootecnia",
}

# CASOS FORA DE ESCOPO DEFINIDOS PELO PROJETO
# FORMATO: (ANO, CURSO_SLUG, NUMERO_QUESTAO)
FORA_ESCOPO = {
    (2023, "arquitetura_e_urbanismo", 16),
}


# ============================================
# UTILIDADES
# ============================================
def slug_para_nome_curso(slug: str) -> str:
    return NOMES_CURSOS.get(slug, slug.replace("_", " ").title().strip())


def extrair_ano_e_curso_da_pasta(nome_pasta: str):
    m = re.match(r"^(\d{4})_(.+)$", nome_pasta)
    if not m:
        raise ValueError(f"Nome de pasta inválido: {nome_pasta}")
    ano = int(m.group(1))
    curso_slug = m.group(2)
    return ano, curso_slug


def montar_nome_pdf(ano: int, tipo: str, curso_slug: str) -> str:
    return f"{ano}_{tipo}_{curso_slug}.pdf"


def montar_url_pdf(ano: int, tipo: str, curso_slug: str) -> str:
    nome_pdf = montar_nome_pdf(ano, tipo, curso_slug)
    return f"https://download.inep.gov.br/enade/provas_e_gabaritos/{nome_pdf}"


def obter_arquivo_questoes(pasta_saida: Path) -> Path:
    arquivos = sorted(pasta_saida.glob("*_questoes.json"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo *_questoes.json encontrado em {pasta_saida}")
    return arquivos[0]


def normalizar_status(status_json: str, ano: int, curso_slug: str, numero: int) -> str:
    if numero == 6:
        return "FORA_ESCOPO"

    if ano == 2023 and eh_fora_escopo_manual_2023(curso_slug, numero):
        return "FORA_ESCOPO"

    if (ano, curso_slug, numero) in FORA_ESCOPO:
        return "FORA_ESCOPO"

    status = (status_json or "").strip().upper()

    mapa = {
        "COMPLETA": "COMPLETA",
        "INCOMPLETA": "INCOMPLETA",
        "NAO_ENCONTRADA": "NAO_ENCONTRADA",
        "NÃO_ENCONTRADA": "NAO_ENCONTRADA",
        "FORA_ESCOPO": "FORA_ESCOPO",
    }

    return mapa.get(status, "INCOMPLETA")


def normalizar_confianca(confianca_json: str | None) -> str | None:
    if not confianca_json:
        return None

    confianca = confianca_json.strip().upper()

    mapa = {
        "ALTA": "ALTA",
        "MEDIA": "MEDIA",
        "MÉDIA": "MEDIA",
        "BAIXA": "BAIXA",
    }

    return mapa.get(confianca)


def carregar_json(caminho_json: Path):
    with open(caminho_json, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================
# BANCO
# ============================================
def conectar_banco(host: str, port: int, dbname: str, user: str, password: str):
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )


def obter_ou_criar_ano(cur, ano: int) -> int:
    cur.execute("SELECT ID FROM ANO WHERE VALOR = %s", (ano,))
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO ANO (VALOR)
        VALUES (%s)
        RETURNING ID
        """,
        (ano,)
    )
    return cur.fetchone()[0]


def obter_ou_criar_curso(cur, curso_slug: str, nome_curso: str) -> int:
    cur.execute("SELECT ID FROM CURSO WHERE SLUG = %s", (curso_slug,))
    row = cur.fetchone()

    if row:
        cur.execute(
            """
            UPDATE CURSO
               SET NOME = %s
             WHERE ID = %s
            """,
            (nome_curso, row[0])
        )
        return row[0]

    nome_legado = curso_slug.replace("_", " ").upper().strip()
    cur.execute(
        """
        SELECT ID
          FROM CURSO
         WHERE NOME IN (%s, %s)
         LIMIT 1
        """,
        (nome_curso, nome_legado)
    )
    row = cur.fetchone()

    if row:
        cur.execute(
            """
            UPDATE CURSO
               SET NOME = %s,
                   SLUG = %s
             WHERE ID = %s
            """,
            (nome_curso, curso_slug, row[0])
        )
        return row[0]

    cur.execute(
        """
        INSERT INTO CURSO (NOME, SLUG)
        VALUES (%s, %s)
        RETURNING ID
        """,
        (nome_curso, curso_slug)
    )
    return cur.fetchone()[0]


def obter_ou_criar_prova(
    cur,
    ano_id: int,
    curso_id: int,
    titulo: str,
    url_pdf_prova: str,
    url_pdf_gabarito: str,
    caminho_pdf_prova: str,
    caminho_pdf_gabarito: str
) -> int:
    cur.execute(
        """
        SELECT ID
        FROM PROVA
        WHERE ANO_ID = %s
          AND CURSO_ID = %s
        """,
        (ano_id, curso_id)
    )
    row = cur.fetchone()

    if row:
        prova_id = row[0]
        cur.execute(
            """
            UPDATE PROVA
               SET TITULO = %s,
                   URL_PDF_PROVA = %s,
                   URL_PDF_GABARITO = %s,
                   CAMINHO_PDF_PROVA = %s,
                   CAMINHO_PDF_GABARITO = %s,
                   VERSAO_PARSER = %s
             WHERE ID = %s
            """,
            (
                titulo,
                url_pdf_prova,
                url_pdf_gabarito,
                caminho_pdf_prova,
                caminho_pdf_gabarito,
                VERSAO_PARSER,
                prova_id,
            )
        )
        return prova_id

    cur.execute(
        """
        INSERT INTO PROVA (
            ANO_ID,
            CURSO_ID,
            TITULO,
            URL_PDF_PROVA,
            URL_PDF_GABARITO,
            CAMINHO_PDF_PROVA,
            CAMINHO_PDF_GABARITO,
            VERSAO_PARSER
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING ID
        """,
        (
            ano_id,
            curso_id,
            titulo,
            url_pdf_prova,
            url_pdf_gabarito,
            caminho_pdf_prova,
            caminho_pdf_gabarito,
            VERSAO_PARSER,
        )
    )
    return cur.fetchone()[0]


def upsert_questao_staging(cur, prova_id: int, ano: int, curso_slug: str, registro: dict):
    numero = int(registro["numero"])
    gabarito = registro.get("gabarito")
    if gabarito and str(gabarito).strip().upper() not in {"A", "B", "C", "D", "E"}:
        gabarito = None
    status = normalizar_status(registro.get("status"), ano, curso_slug, numero)
    confianca = normalizar_confianca(registro.get("confianca"))
    parse_strategy = registro.get("parse_strategy")
    enunciado = registro.get("enunciado")
    alternativas = registro.get("alternativas") or {}
    alternativas_completas = bool(registro.get("alternativas_completas", False))
    texto_bruto = registro.get("texto_bruto")
    observacao = None

    if status == "FORA_ESCOPO":
        observacao = "QUESTAO FORA DO ESCOPO DO PROJETO"

    cur.execute(
        """
        INSERT INTO QUESTAO_STAGING (
            PROVA_ID,
            NUMERO,
            GABARITO_RESPOSTA,
            STATUS,
            CONFIANCA,
            PARSE_STRATEGY,
            ENUNCIADO,
            ALTERNATIVA_A,
            ALTERNATIVA_B,
            ALTERNATIVA_C,
            ALTERNATIVA_D,
            ALTERNATIVA_E,
            ALTERNATIVAS_COMPLETAS,
            TEXTO_BRUTO,
            OBSERVACAO,
            VERSAO_PARSER
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (PROVA_ID, NUMERO, VERSAO_PARSER)
        DO UPDATE SET
            GABARITO_RESPOSTA = EXCLUDED.GABARITO_RESPOSTA,
            STATUS = EXCLUDED.STATUS,
            CONFIANCA = EXCLUDED.CONFIANCA,
            PARSE_STRATEGY = EXCLUDED.PARSE_STRATEGY,
            ENUNCIADO = EXCLUDED.ENUNCIADO,
            ALTERNATIVA_A = EXCLUDED.ALTERNATIVA_A,
            ALTERNATIVA_B = EXCLUDED.ALTERNATIVA_B,
            ALTERNATIVA_C = EXCLUDED.ALTERNATIVA_C,
            ALTERNATIVA_D = EXCLUDED.ALTERNATIVA_D,
            ALTERNATIVA_E = EXCLUDED.ALTERNATIVA_E,
            ALTERNATIVAS_COMPLETAS = EXCLUDED.ALTERNATIVAS_COMPLETAS,
            TEXTO_BRUTO = EXCLUDED.TEXTO_BRUTO,
            OBSERVACAO = EXCLUDED.OBSERVACAO
        """,
        (
            prova_id,
            numero,
            gabarito,
            status,
            confianca,
            parse_strategy,
            enunciado,
            alternativas.get("A"),
            alternativas.get("B"),
            alternativas.get("C"),
            alternativas.get("D"),
            alternativas.get("E"),
            alternativas_completas,
            texto_bruto,
            observacao,
            VERSAO_PARSER,
        )
    )


# ============================================
# PROCESSAMENTO
# ============================================
def processar_pasta(cur, pasta_saida: Path, pasta_pdfs: Path):
    ano, curso_slug = extrair_ano_e_curso_da_pasta(pasta_saida.name)
    nome_curso = slug_para_nome_curso(curso_slug)

    arquivo_json = obter_arquivo_questoes(pasta_saida)
    dados = carregar_json(arquivo_json)

    nome_pdf_prova = montar_nome_pdf(ano, "PV", curso_slug)
    nome_pdf_gabarito = montar_nome_pdf(ano, "GB", curso_slug)

    caminho_pdf_prova = str((pasta_pdfs / nome_pdf_prova).resolve())
    caminho_pdf_gabarito = str((pasta_pdfs / nome_pdf_gabarito).resolve())

    url_pdf_prova = montar_url_pdf(ano, "PV", curso_slug)
    url_pdf_gabarito = montar_url_pdf(ano, "GB", curso_slug)

    titulo = f"ENADE {ano} - {nome_curso}"

    ano_id = obter_ou_criar_ano(cur, ano)
    curso_id = obter_ou_criar_curso(cur, curso_slug, nome_curso)
    prova_id = obter_ou_criar_prova(
        cur,
        ano_id,
        curso_id,
        titulo,
        url_pdf_prova,
        url_pdf_gabarito,
        caminho_pdf_prova,
        caminho_pdf_gabarito
    )

    total = 0
    for registro in dados:
        upsert_questao_staging(cur, prova_id, ano, curso_slug, registro)
        total += 1

    print(f"OK - {pasta_saida.name}: {total} QUESTOES CARREGADAS")


def main():
    parser = argparse.ArgumentParser(
        description="CARREGA JSONS DA V2 PARA A TABELA QUESTAO_STAGING"
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=5432, type=int)
    parser.add_argument("--dbname", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument(
        "--output-root",
        default=None,
        help="PASTA RAIZ DO OUTPUT V2. EX.: OUTPUT/V2"
    )
    parser.add_argument(
        "--somente-pasta",
        default=None,
        help="NOME DE UMA PASTA ESPECIFICA. EX.: 2023_AGRONOMIA"
    )

    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    pasta_output_v2 = Path(args.output_root) if args.output_root else root / "output" / "v2"
    pasta_pdfs = root / "pdfs"

    if not pasta_output_v2.exists():
        raise FileNotFoundError(f"PASTA NAO ENCONTRADA: {pasta_output_v2}")

    conn = conectar_banco(
        host=args.host,
        port=args.port,
        dbname=args.dbname,
        user=args.user,
        password=args.password
    )

    try:
        with conn:
            with conn.cursor() as cur:
                if args.somente_pasta:
                    pasta = pasta_output_v2 / args.somente_pasta
                    if not pasta.exists():
                        raise FileNotFoundError(f"PASTA NAO ENCONTRADA: {pasta}")
                    processar_pasta(cur, pasta, pasta_pdfs)
                else:
                    pastas = sorted([p for p in pasta_output_v2.iterdir() if p.is_dir()])
                    if not pastas:
                        raise FileNotFoundError(f"NENHUMA PASTA DE CURSO ENCONTRADA EM: {pasta_output_v2}")

                    for pasta in pastas:
                        processar_pasta(cur, pasta, pasta_pdfs)

        print("\nCARGA FINALIZADA COM SUCESSO")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
