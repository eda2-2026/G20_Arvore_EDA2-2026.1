import os
import csv
import random
import matplotlib.pyplot as plt
from typing import List, Dict, Any

from trees import AVL, RedBlackTree
from models import Intervalo
from main import gerar_consultas, rodar_benchmark_arvore

def executar_e_salvar_benchmarks(salvar_graficos: bool = True, salvar_csv: bool = True):
    print("Iniciando Benchmarks de Desempenho para Árvores de Intervalos...")
    os.makedirs("graficos", exist_ok=True)

    tamanhos_aleatorio = [100, 500, 1000, 2000, 5000, 10000]
    tamanhos_ordenado = [100, 250, 500, 1000, 2000, 4000]
    arvores = {"AVL": AVL, "Red-Black": RedBlackTree}
    resultados: List[Dict[str, Any]] = []

    for cenario_ordenado in [False, True]:
        tipo_cenario = "Ordenado" if cenario_ordenado else "Aleatorio"
        tamanhos = tamanhos_ordenado if cenario_ordenado else tamanhos_aleatorio
        print(f"\n--- Cenário: {tipo_cenario} ---")

        for n in tamanhos:
            print(f"Executando para N = {n}...")
            random.seed(42)
            consultas = gerar_consultas(n, ordenado=cenario_ordenado, seed=42)

            intervalos_existentes = [consulta.intervalo for consulta in random.sample(consultas, max(1, min(5, len(consultas))))]
            intervalos_inexistentes = [Intervalo(inicio=n * 5 + i * 10, fim=n * 5 + i * 10 + 3) for i in range(max(1, min(5, len(consultas))))]
            intervalos_busca = intervalos_existentes + intervalos_inexistentes
            random.shuffle(intervalos_busca)

            consultas_remocao = random.sample(consultas, max(1, min(len(consultas), n // 20)))

            for nome_arvore, classe_arvore in arvores.items():
                res = rodar_benchmark_arvore(classe_arvore, consultas, intervalos_busca, consultas_remocao)
                resultados.append({
                    "Cenario": tipo_cenario,
                    "N": n,
                    "Arvore": nome_arvore,
                    "TempoInsercao_ms": res["tempo_insercao"] * 1000,
                    "TempoBusca_ms": res["tempo_busca"] * 1000,
                    "TempoRemocao_ms": res["tempo_remocao"] * 1000,
                    "Altura": res["altura"],
                })

    if salvar_csv and resultados:
        caminho_csv = os.path.join("graficos", "resultados_benchmark.csv")
        with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
        print(f"\nResultados salvos com sucesso em: {caminho_csv}")

    if salvar_graficos:
        gerar_graficos(resultados)
        
def gerar_graficos(resultados: List[Dict[str, Any]]):
    arvores_nomes = ["AVL", "Red-Black"]
    cores = {"AVL": "green", "Red-Black": "red"}
    estilos = {"AVL": "-^", "Red-Black": "-s"}

    for cenario in ["Aleatorio", "Ordenado"]:
        dados_cenario = [r for r in resultados if r["Cenario"] == cenario]
        n_valores = sorted(list(set(r["N"] for r in dados_cenario)))

        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Benchmark de Desempenho - Entrada: {cenario}", fontsize=16, fontweight='bold')

        metricas = [
            ("Altura", "Altura da Árvore", axs[0, 0], "Altura (Nível)"),
            ("TempoInsercao_ms", "Tempo de Inserção", axs[0, 1], "Tempo (ms)"),
            ("TempoBusca_ms", "Tempo de Busca", axs[1, 0], "Tempo (ms)"),
            ("TempoRemocao_ms", "Tempo de Remoção", axs[1, 1], "Tempo (ms)"),
        ]

        for metrica_chave, titulo, ax, ylabel in metricas:
            for nome_arvore in arvores_nomes:
                x = []
                y = []
                for n in n_valores:
                    for r in dados_cenario:
                        if r["Arvore"] == nome_arvore and r["N"] == n:
                            x.append(n)
                            y.append(r[metrica_chave])
                            break
                ax.plot(x, y, estilos[nome_arvore], label=nome_arvore, color=cores[nome_arvore])

            ax.set_title(titulo, fontsize=12, fontweight='bold')
            ax.set_xlabel("N (Quantidade de Consultas)", fontsize=10)
            ax.set_ylabel(ylabel, fontsize=10)
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.legend()

        plt.tight_layout()
        nome_arquivo = f"benchmark_arvores_{cenario.lower()}.png"
        caminho_grafico = os.path.join("graficos", nome_arquivo)
        plt.savefig(caminho_grafico, dpi=300)
        plt.close()
        print(f"Gráfico salvo com sucesso em: {caminho_grafico}")

if __name__ == "__main__":
    executar_e_salvar_benchmarks(salvar_graficos=True, salvar_csv=True)
