import csv
import json
import random
import time
from pathlib import Path
from typing import List, Dict, Any, Type

from models import Consulta, Intervalo


def gerar_consultas(tamanho: int, ordenado: bool = False, seed: int = None) -> List[Consulta]:
    """Gera consultas de agendamento com intervalos não sobrepostos."""
    if seed is not None:
        random.seed(seed)

    duracao_max = 4
    consultas: List[Consulta] = []

    for idx in range(1, tamanho + 1):
        inicio = (idx - 1) * 6
        duracao = random.randint(1, duracao_max)
        consultas.append(
            Consulta(
                id_consulta=idx,
                cidadao=f"Cidadao_{idx}",
                intervalo=Intervalo(inicio=inicio, fim=inicio + duracao),
            )
        )

    if not ordenado:
        random.shuffle(consultas)

    return consultas


def rodar_benchmark_arvore(
    tree_class: Type,
    consultas: List[Consulta],
    intervalos_busca: List[Intervalo],
    consultas_remocao: List[Consulta]
) -> Dict[str, Any]:
    """Executa benchmark de inserção, busca e remoção em uma árvore de intervalos."""
    arvore = tree_class()

    inicio = time.perf_counter()
    for consulta in consultas:
        arvore.inserir(consulta)
    tempo_insercao = time.perf_counter() - inicio

    altura_final = arvore.altura()

    inicio = time.perf_counter()
    for intervalo in intervalos_busca:
        arvore.buscar_conflito(intervalo)
    tempo_busca = time.perf_counter() - inicio

    inicio = time.perf_counter()
    for consulta in consultas_remocao:
        arvore.remover(consulta)
    tempo_remocao = time.perf_counter() - inicio

    return {
        "tempo_insercao": tempo_insercao,
        "tempo_busca": tempo_busca,
        "tempo_remocao": tempo_remocao,
        "altura": altura_final,
        "rotacoes": arvore.rotacoes,
        "tamanho": arvore.tamanho(),
    }

def exportar_benchmark_csv(resultados: List[Dict[str, Any]], caminho: Path) -> None:
    """Exporta resultados de benchmark para CSV."""
    if not resultados:
        return
    import csv
    with caminho.open("w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
        writer.writeheader()
        writer.writerows(resultados)
    print(f"Resultados exportados para {caminho}")

def exportar_benchmark_json(resultados: List[Dict[str, Any]], caminho: Path) -> None:
    """Exporta resultados de benchmark para JSON."""
    import json
    with caminho.open("w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print(f"Resultados exportados para {caminho}")
