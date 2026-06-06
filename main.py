import argparse
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from models import Consulta, Intervalo
from trees import AVL, RedBlackTree


def imprimir_cabecalho(titulo: str):
    print()
    print("=" * 60)
    print(f"{titulo.center(60)}")
    print("=" * 60)
    print()


def gerar_consultas(tamanho: int, ordenado: bool = False, seed: int = None) -> List[Consulta]:
    """Gera consultas de agendamento com intervalos de tempo."""
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


AGENDA_FILE = Path(__file__).resolve().parent / "agenda.json"


def consulta_para_dict(consulta: Consulta) -> Dict[str, Any]:
    return {
        "id_consulta": consulta.id_consulta,
        "cidadao": consulta.cidadao,
        "intervalo": {
            "inicio": consulta.intervalo.inicio,
            "fim": consulta.intervalo.fim,
        },
    }


def consulta_de_dict(data: Dict[str, Any]) -> Consulta:
    intervalo = data["intervalo"]
    return Consulta(
        id_consulta=int(data["id_consulta"]),
        cidadao=str(data["cidadao"]),
        intervalo=Intervalo(inicio=int(intervalo["inicio"]), fim=int(intervalo["fim"])),
    )


def salvar_agenda(consultas: List[Consulta], caminho: Path = AGENDA_FILE) -> None:
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump([consulta_para_dict(c) for c in consultas], arquivo, indent=2, ensure_ascii=False)
    print(f"Agenda salva em {caminho}")


def carregar_agenda(caminho: Path = AGENDA_FILE) -> List[Consulta]:
    if not caminho.exists():
        return []
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    consultas: List[Consulta] = []
    for item in dados:
        try:
            consultas.append(consulta_de_dict(item))
        except Exception as err:
            print(f"Aviso: não foi possível carregar um registro do arquivo de agenda: {err}")
    return consultas


def construir_arvore_por_consultas(consultas: List[Consulta], tree_class: Type) -> Any:
    arvore = tree_class()
    for consulta in consultas:
        arvore.inserir(consulta)
    return arvore


def solicitar_inteiro(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Valor inválido. Digite um número inteiro.")


def rodar_benchmark_arvore(
    tree_class: Type,
    consultas: List[Consulta],
    intervalos_busca: List[Intervalo],
    consultas_remocao: List[Consulta]
) -> Dict[str, Any]:
    """Executa benchmark de inserção, busca e remoção em uma árvore de intervalos."""
    arvore = tree_class()

    inicio = __import__("time").perf_counter()
    for consulta in consultas:
        arvore.inserir(consulta)
    tempo_insercao = __import__("time").perf_counter() - inicio

    altura_final = arvore.altura()

    inicio = __import__("time").perf_counter()
    for intervalo in intervalos_busca:
        arvore.buscar_conflito(intervalo)
    tempo_busca = __import__("time").perf_counter() - inicio

    inicio = __import__("time").perf_counter()
    for consulta in consultas_remocao:
        arvore.remover(consulta)
    tempo_remocao = __import__("time").perf_counter() - inicio

    return {
        "tempo_insercao": tempo_insercao,
        "tempo_busca": tempo_busca,
        "tempo_remocao": tempo_remocao,
        "altura": altura_final,
    }


def executar_cenario_a(n: int, seed: int):
    """Cenário A: Alta Escrita com Verificação de Conflitos."""
    imprimir_cabecalho(f"Cenário A: Alta Escrita (N = {n})")
    print(f"Gerando {n} consultas de agendamento aleatórias com seed {seed}...")

    consultas = gerar_consultas(n, ordenado=False, seed=seed)
    intervalos_existentes = [consulta.intervalo for consulta in random.sample(consultas, min(5, len(consultas)))]
    intervalos_livres = [Intervalo(inicio=n * 5 + i * 10, fim=n * 5 + i * 10 + 5) for i in range(5)]
    intervalos_teste = intervalos_existentes + intervalos_livres
    random.shuffle(intervalos_teste)

    print("Resumo do cenário:")
    print(f"  - Consultas geradas: {len(consultas)}")
    print(f"  - Intervalos de teste: {len(intervalos_teste)} ({len(intervalos_existentes)} existentes + {len(intervalos_livres)} livres)")

    arvores = {
        "AVL (Árvore de Intervalos AVL)": AVL,
        "Red-Black (Árvore de Intervalos Rubro-Negra)": RedBlackTree,
    }

    for nome, classe_arvore in arvores.items():
        print("\n" + "-" * 60)
        print(f"Árvore: {nome}")
        print("-" * 60)
        arvore = classe_arvore()
        insercoes_sucesso = 0

        for consulta in consultas:
            if arvore.inserir(consulta):
                insercoes_sucesso += 1

        print(f"Inserções bem-sucedidas: {insercoes_sucesso} / {n}")
        print(f"Altura final da árvore: {arvore.altura()}")

        print("\nResultados de busca de intervalos de teste:")
        for intervalo in intervalos_teste:
            conflito = arvore.buscar_conflito(intervalo)
            status = "Disponível" if conflito is None else f"Conflito com {conflito}"
            print(f"  - {intervalo}: {status}")


def executar_cenario_b(n: int, seed: int):
    """Cenário B: Alta Leitura com muitas verificações de disponibilidade."""
    imprimir_cabecalho(f"Cenário B: Alta Leitura (N = {n})")
    print(f"Gerando {n} consultas de agendamento ordenadas com seed {seed}...")

    consultas = gerar_consultas(n, ordenado=True, seed=seed)
    intervalos_busca = [
        Intervalo(
            inicio=inicio,
            fim=inicio + random.randint(1, 10)
        )
        for inicio in [random.randint(0, n * 5) for _ in range(200)]
    ]
    arvores = {"AVL": AVL, "Red-Black": RedBlackTree}

    print("Resumo do cenário:")
    print(f"  - Consultas geradas: {len(consultas)}")
    print(f"  - Intervalos de busca: {len(intervalos_busca)}")
    print("\nResultado do benchmark de leitura:")
    print("| Árvore      | Altura | Tamanho | Inserção (ms) | Busca (200) (ms) | Rotações |")
    print("|-------------|--------|---------|---------------|------------------|----------|")

    for nome, classe_arvore in arvores.items():
        res = rodar_benchmark_arvore(classe_arvore, consultas, intervalos_busca, [])
        print(f"| {nome:11s} | {res['altura']:6d} | {res['tamanho']:7d} | {res['tempo_insercao']*1000:13.3f} | {res['tempo_busca']*1000:16.3f} | {res['rotacoes']:8d} |")


def executar_cenario_c(n: int, seed: int):
    """Cenário C: Fluxo Misto com inserções, buscas e remoções."""
    imprimir_cabecalho(f"Cenário C: Fluxo Misto (N = {n})")
    print(f"Gerando {n} consultas de agendamento aleatórias com seed {seed}...")

    consultas = gerar_consultas(n, ordenado=False, seed=seed)
    consultas_remocao = random.sample(consultas, min(max(1, n // 10), len(consultas)))
    arvores = {"AVL": AVL, "Red-Black": RedBlackTree}

    print("Resumo do cenário:")
    print(f"  - Consultas geradas: {len(consultas)}")
    print(f"  - Consultas removidas: {len(consultas_remocao)}")
    print("\nResultado do benchmark misto:")
    print("| Árvore      | Altura Ini | Altura Fim | Tamanho Fim | Remoção (ms) | Rotações Total |")
    print("|-------------|------------|------------|-------------|--------------|----------------|")

    for nome, classe_arvore in arvores.items():
        arvore = classe_arvore()
        for consulta in consultas:
            arvore.inserir(consulta)

        altura_ini = arvore.altura()
        inicio = __import__("time").perf_counter()
        for consulta in consultas_remocao:
            arvore.remover(consulta)
        tempo = __import__("time").perf_counter() - inicio

        altura_fim = arvore.altura()
        tamanho_fim = arvore.tamanho()
        print(f"| {nome:11s} | {altura_ini:10d} | {altura_fim:10d} | {tamanho_fim:11d} | {tempo*1000:12.3f} | {arvore.rotacoes:14d} |")


def executar_benchmark_completo(n: int, seed: int, export_format: Optional[str] = None):
    """Benchmark comparativo das Árvores de Intervalos."""
    imprimir_cabecalho(f"Benchmark Comparativo Geral (N = {n})")

    consultas = gerar_consultas(n, ordenado=False, seed=seed)
    intervalos_busca = [
        Intervalo(
            inicio=inicio,
            fim=inicio + random.randint(1, 10)
        )
        for inicio in [random.randint(0, n * 5) for _ in range(500)]
    ]
    consultas_remocao = random.sample(consultas, min(n, 200))
    arvores = {"AVL": AVL, "Red-Black": RedBlackTree}

    print("Resumo do benchmark:")
    print(f"  - Consultas geradas: {len(consultas)}")
    print(f"  - Intervalos de busca: {len(intervalos_busca)}")
    print(f"  - Consultas removidas: {len(consultas_remocao)}")
    print("\nTabela comparativa:")
    print("| Árvore      | Altura | Tamanho | Inserção (ms) | Busca (500) (ms) | Remoção (200) (ms) | Rotações |")
    print("|-------------|--------|---------|---------------|------------------|--------------------|----------|")

    resultados_export = []
    from utils import exportar_benchmark_csv, exportar_benchmark_json
    from pathlib import Path

    for nome, classe_arvore in arvores.items():
        res = rodar_benchmark_arvore(classe_arvore, consultas, intervalos_busca, consultas_remocao)
        print(f"| {nome:11s} | {res['altura']:6d} | {res['tamanho']:7d} | {res['tempo_insercao']*1000:13.3f} | {res['tempo_busca']*1000:16.3f} | {res['tempo_remocao']*1000:18.3f} | {res['rotacoes']:8d} |")
        res["arvore"] = nome
        resultados_export.append(res)
        
    if export_format == "csv":
        exportar_benchmark_csv(resultados_export, Path("benchmark_results.csv"))
    elif export_format == "json":
        exportar_benchmark_json(resultados_export, Path("benchmark_results.json"))


def executar_cenario_d(n: int, seed: int):
    """Cenário D: Comparação Ordenado vs Aleatório.
    Mostra impacto da ordem de inserção em altura e rotações."""
    imprimir_cabecalho(f"Cenário D: Ordenado vs Aleatório (N = {n})")
    
    consultas_ordenadas = gerar_consultas(n, ordenado=True, seed=seed)
    consultas_aleatorias = gerar_consultas(n, ordenado=False, seed=seed)
    arvores = {"AVL": AVL, "Red-Black": RedBlackTree}
    
    print("\nTabela comparativa (Inserção):")
    print("| Árvore      | Ordem     | Altura | Tamanho | Inserção (ms) | Rotações |")
    print("|-------------|-----------|--------|---------|---------------|----------|")
    
    for nome, classe_arvore in arvores.items():
        res_ord = rodar_benchmark_arvore(classe_arvore, consultas_ordenadas, [], [])
        print(f"| {nome:11s} | Ordenada  | {res_ord['altura']:6d} | {res_ord['tamanho']:7d} | {res_ord['tempo_insercao']*1000:13.3f} | {res_ord['rotacoes']:8d} |")
        
        res_ale = rodar_benchmark_arvore(classe_arvore, consultas_aleatorias, [], [])
        print(f"| {nome:11s} | Aleatória | {res_ale['altura']:6d} | {res_ale['tamanho']:7d} | {res_ale['tempo_insercao']*1000:13.3f} | {res_ale['rotacoes']:8d} |")


def executar_todos_cenarios(n: int, seed: int, export_format: Optional[str] = None):
    imprimir_cabecalho(f"Executando todos os cenários (N = {n})")
    executar_cenario_a(n, seed)
    executar_cenario_b(n, seed)
    executar_cenario_c(n, seed)
    executar_cenario_d(n, seed)
    executar_benchmark_completo(n, seed, export_format)


def imprimir_menu_interativo() -> None:
    print("\nModo Interativo de Agendamento")
    print("1 - Mostrar agendamentos")
    print("2 - Adicionar consulta")
    print("3 - Remover consulta")
    print("4 - Buscar conflito de intervalo")
    print("5 - Trocar tipo de árvore")
    print("6 - Salvar agenda")
    print("0 - Sair")


def imprimir_agendamentos(arvore) -> None:
    consultas = arvore.em_ordem()
    if not consultas:
        print("Nenhuma consulta agendada.")
        return

    print("\nAgendamentos atuais:")
    for consulta in consultas:
        print(f"  - ID {consulta.id_consulta}: {consulta.cidadao} | {consulta.intervalo}")


def solicitar_intervalo() -> Intervalo:
    inicio = solicitar_inteiro("Informe o início do intervalo: ")
    fim = solicitar_inteiro("Informe o fim do intervalo: ")
    return Intervalo(inicio=inicio, fim=fim)


def executar_interativo(n: int, seed: int, tree_choice: Optional[str] = None):
    imprimir_cabecalho("Modo Interativo de Agendamento")

    consultas = carregar_agenda()
    if consultas:
        print(f"Agenda carregada de {len(consultas)} consultas salvas.")
    else:
        print("Nenhuma agenda salva encontrada. Iniciando agenda vazia.")

    tree_type = tree_choice or "AVL"
    if tree_choice is None:
        print("\nEscolha o tipo de árvore para o modo interativo:")
        print("1 - AVL")
        print("2 - Red-Black")
        escolha_tree = input("Tipo de árvore [1/2] (padrão 1): ").strip() or "1"
        tree_type = "RB" if escolha_tree == "2" else "AVL"

    tree_class = AVL if tree_type == "AVL" else RedBlackTree
    arvore = construir_arvore_por_consultas(consultas, tree_class)
    print(f"Usando árvore {tree_type}.")
    imprimir_agendamentos(arvore)

    while True:
        imprimir_menu_interativo()
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Saindo do modo interativo.")
            break
        elif escolha == "1":
            imprimir_agendamentos(arvore)
        elif escolha == "2":
            try:
                id_consulta = solicitar_inteiro("Informe o ID da consulta: ")
                if any(c.id_consulta == id_consulta for c in consultas):
                    print(f"Já existe uma consulta com ID {id_consulta}. Use outro ID.")
                    continue
                cidadao = input("Informe o nome do cidadão: ").strip()
                intervalo = solicitar_intervalo()
                consulta = Consulta(id_consulta=id_consulta, cidadao=cidadao, intervalo=intervalo)
                if arvore.inserir(consulta):
                    consultas.append(consulta)
                    salvar_agenda(consultas)
                    print(f"Consulta adicionada com sucesso: {consulta}")
                else:
                    print(f"Falha: conflito encontrado para o intervalo {intervalo}.")
            except ValueError as err:
                print(f"Entrada inválida: {err}")
        elif escolha == "3":
            try:
                id_consulta = solicitar_inteiro("Informe o ID da consulta a remover: ")
                inicio = solicitar_inteiro("Informe o início do intervalo da consulta a remover: ")
                consulta_remover = next(
                    (c for c in consultas if c.id_consulta == id_consulta and c.intervalo.inicio == inicio),
                    None,
                )
                if consulta_remover is None:
                    print("Não foi possível encontrar a consulta para remoção.")
                    continue
                if arvore.remover(consulta_remover):
                    consultas.remove(consulta_remover)
                    salvar_agenda(consultas)
                    print(f"Consulta removida: {consulta_remover}")
                else:
                    print(f"Não foi possível remover. Verifique se o ID e o início estão corretos.")
            except ValueError as err:
                print(f"Entrada inválida: {err}")
        elif escolha == "4":
            try:
                intervalo = solicitar_intervalo()
                conflito = arvore.buscar_conflito(intervalo)
                if conflito is None:
                    print(f"Intervalo {intervalo} está disponível.")
                else:
                    print(f"Intervalo {intervalo} conflita com {conflito}")
            except ValueError as err:
                print(f"Entrada inválida: {err}")
        elif escolha == "5":
            print("\nEscolha tipo de árvore:")
            print("1 - AVL")
            print("2 - Red-Black")
            escolha_tree = input("Tipo de árvore [1/2]: ").strip() or "1"
            tree_type = "RB" if escolha_tree == "2" else "AVL"
            tree_class = AVL if tree_type == "AVL" else RedBlackTree
            arvore = construir_arvore_por_consultas(consultas, tree_class)
            print(f"Árvore alterada para {tree_type}.")
        elif escolha == "6":
            salvar_agenda(consultas)
        else:
            print("Opção inválida. Digite 0, 1, 2, 3, 4, 5 ou 6.")


def main():
    parser = argparse.ArgumentParser(description="Simulador de Agendamento com Árvores de Intervalos AVL e Rubro-Negra")
    parser.add_argument("-n", type=int, default=5000, help="Quantidade de consultas a processar")
    parser.add_argument("-s", type=int, default=123, help="Seed para geração de números pseudo-aleatórios")
    parser.add_argument("-c", type=str, default="all", choices=["all", "A", "B", "C", "D", "benchmark", "in"], 
                        help="Cenário de teste: all (Todos), A (Alta Escrita), B (Alta Leitura), C (Fluxo Misto), D (Ordenado vs Aleatório), benchmark (Comparativo), in (Agendamento manual)")
    parser.add_argument("--tree", type=str, default="AVL", choices=["AVL", "RB"],
                        help="Tipo de árvore usada no modo interativo: AVL ou RB (Red-Black)")
    parser.add_argument("--export", type=str, default=None, choices=["csv", "json"],
                        help="Exporta resultados do benchmark para arquivo")

    args = parser.parse_args()

    if args.c == "all":
        executar_todos_cenarios(args.n, args.s, args.export)
    elif args.c == "A":
        executar_cenario_a(args.n, args.s)
    elif args.c == "B":
        executar_cenario_b(args.n, args.s)
    elif args.c == "C":
        executar_cenario_c(args.n, args.s)
    elif args.c == "D":
        executar_cenario_d(args.n, args.s)
    elif args.c == "in":
        executar_interativo(args.n, args.s, args.tree)
    else:
        executar_benchmark_completo(args.n, args.s, args.export)


if __name__ == "__main__":
    main()
