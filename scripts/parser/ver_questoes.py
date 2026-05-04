import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARQUIVO = ROOT / "output" / "v2" / "2023_agronomia" / "2023_pv_agronomia_questoes.json"

with open(ARQUIVO, "r", encoding="utf-8") as f:
    dados = json.load(f)

for q in dados:
    if 1 <= q["numero"] <= 5:
        print("=" * 120)
        print(f"QUESTAO: {q['numero']}")
        print(f"GABARITO: {q['gabarito']}")
        print(f"STATUS: {q.get('status')}")
        print(f"OBSERVACAO: {q.get('observacao')}")
        print()

        print("ENUNCIADO:\n")
        print(q["enunciado"])

        print("\nA:\n")
        print(q["alternativas"].get("A", ""))

        print("\nB:\n")
        print(q["alternativas"].get("B", ""))

        print("\nC:\n")
        print(q["alternativas"].get("C", ""))

        print("\nD:\n")
        print(q["alternativas"].get("D", ""))

        print("\nE:\n")
        print(q["alternativas"].get("E", ""))
        print()