FORA_ESCOPO_MANUAL_2023 = {
    "engenharia_civil": {
        12, 17, 18, 19, 20, 21, 22, 25, 28, 29, 30, 33, 35, 36, 37, 38,
    },
    "engenharia_de_alimentos": {
        13, 15, 17, 18, 20, 21, 26, 27, 29, 33, 35, 37,
    },
    "engenharia_da_computacao": {
        10, 12, 13, 19, 22, 23, 24, 25, 29, 30, 32,
    },
    "engenharia_de_controle_e_automacao": {
        10, 12, 15, 16, 17, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31,
        32, 34, 36, 37, 38,
    },
    "engenharia_de_producao": {
        12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 30,
        32, 33, 35, 37, 38,
    },
    "engenharia_eletrica": {
        10, 11, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
        29, 31, 33, 34, 35, 36, 37,
    },
    "engenharia_florestal": {
        16, 17, 27, 29, 30, 32, 33, 35, 36, 37,
    },
    "engenharia_mecanica": {
        10, 11, 16, 17, 18, 20, 21, 22, 23, 24, 25, 27, 30, 35, 36, 37,
        38,
    },
    "engenharia_quimica": {
        10, 13, 14, 15, 16, 17, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29,
        30, 31, 32, 33, 35, 37, 38,
    },
    "farmacia": {
        20, 21, 22, 23, 24, 26, 27, 30, 33, 35,
    },
    "fisioterapia": {
        10, 17, 23, 27, 34,
    },
}


def eh_fora_escopo_manual_2023(curso_slug: str | None, numero: int) -> bool:
    if not curso_slug:
        return False

    return numero in FORA_ESCOPO_MANUAL_2023.get(curso_slug, set())
