import pytest
import random
from models import Consulta, Intervalo
from trees import AVL, RedBlackTree

# Valida propriedades de uma árvore de pesquisa binária e de balanceamento

def is_valid_search_tree(nodo, min_val=float('-inf'), max_val=float('inf')) -> bool:
    if nodo is None or getattr(nodo, 'intervalo', None) is None:
        return True

    chave = nodo.intervalo.inicio
    if chave <= min_val or chave >= max_val:
        return False

    return (is_valid_search_tree(nodo.esquerda, min_val, chave) and \
            is_valid_search_tree(nodo.direita, chave, max_val))


def get_avl_height_and_validate(nodo) -> tuple[bool, int]:
    if nodo is None:
        return True, 0

    ok_esq, alt_esq = get_avl_height_and_validate(nodo.esquerda)
    ok_dir, alt_dir = get_avl_height_and_validate(nodo.direita)

    if not ok_esq or not ok_dir:
        return False, 0

    if abs(alt_esq - alt_dir) > 1:
        return False, 0

    if nodo.altura != 1 + max(alt_esq, alt_dir):
        return False, 0

    return True, 1 + max(alt_esq, alt_dir)


def is_valid_avl(tree: AVL) -> bool:
    if not is_valid_search_tree(tree.raiz):
        return False
    ok, _ = get_avl_height_and_validate(tree.raiz)
    return ok


def validate_rb_properties(tree: RedBlackTree) -> tuple[bool, int]:
    if tree.raiz != tree.NIL and tree.raiz.color is True:
        return False, 0

    def check_node(nodo) -> tuple[bool, int]:
        if nodo == tree.NIL or nodo is None:
            return True, 1

        if nodo.color is True:
            if (nodo.esquerda != tree.NIL and nodo.esquerda.color is True) or \
               (nodo.direita != tree.NIL and nodo.direita.color is True):
                return False, 0

        ok_esq, pretos_esq = check_node(nodo.esquerda)
        ok_dir, pretos_dir = check_node(nodo.direita)

        if not ok_esq or not ok_dir:
            return False, 0

        if pretos_esq != pretos_dir:
            return False, 0

        return True, pretos_esq + (1 if nodo.color is False else 0)

    ok, _ = check_node(tree.raiz)
    return ok, 0


def is_valid_rb(tree: RedBlackTree) -> bool:
    def is_valid_search_tree_rb(nodo, min_val=float('-inf'), max_val=float('inf')) -> bool:
        if nodo == tree.NIL or nodo is None:
            return True

        chave = nodo.intervalo.inicio
        if chave <= min_val or chave >= max_val:
            return False
        return (is_valid_search_tree_rb(nodo.esquerda, min_val, chave) and \
                is_valid_search_tree_rb(nodo.direita, chave, max_val))

    if not is_valid_search_tree_rb(tree.raiz):
        return False
    ok, _ = validate_rb_properties(tree)
    return ok


@pytest.mark.parametrize("tree_class, validator", [
    (AVL, is_valid_avl),
    (RedBlackTree, is_valid_rb)
])
def test_insercao_e_busca(tree_class, validator):
    tree = tree_class()
    consultas = [
        Consulta(1, "Maria", Intervalo(1, 4)),
        Consulta(2, "João", Intervalo(5, 8)),
        Consulta(3, "Ana", Intervalo(9, 12)),
        Consulta(4, "Paulo", Intervalo(13, 16)),
        Consulta(5, "Luiza", Intervalo(17, 20)),
    ]

    for consulta in consultas:
        assert tree.inserir(consulta)
        assert validator(tree)

    for consulta in consultas:
        encontrado = tree.buscar_conflito(consulta.intervalo)
        assert encontrado is not None
        assert encontrado.id_consulta == consulta.id_consulta

    intervalo_livre = Intervalo(1000, 1010)
    assert tree.buscar_conflito(intervalo_livre) is None


@pytest.mark.parametrize("tree_class, validator", [
    (AVL, is_valid_avl),
    (RedBlackTree, is_valid_rb)
])
def test_remocao(tree_class, validator):
    tree = tree_class()
    consultas = [
        Consulta(i, f"Pessoa_{i}", Intervalo((i - 1) * 3, (i - 1) * 3 + 2))
        for i in range(1, 11)
    ]

    for consulta in consultas:
        assert tree.inserir(consulta)

    random.seed(42)
    random.shuffle(consultas)

    for consulta in consultas:
        assert tree.remover(consulta)
        assert tree.buscar_conflito(consulta.intervalo) is None
        assert validator(tree)


@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_travessia_em_ordem(tree_class):
    tree = tree_class()
    consultas = [
        Consulta(1, "A", Intervalo(50, 53)),
        Consulta(2, "B", Intervalo(30, 33)),
        Consulta(3, "C", Intervalo(70, 73)),
        Consulta(4, "D", Intervalo(20, 23)),
        Consulta(5, "E", Intervalo(40, 43)),
        Consulta(6, "F", Intervalo(60, 63)),
        Consulta(7, "G", Intervalo(80, 83)),
    ]

    for consulta in consultas:
        assert tree.inserir(consulta)

    registros = tree.em_ordem()
    chaves_ordenadas = [consulta.intervalo.inicio for consulta in registros]
    assert chaves_ordenadas == sorted(chaves_ordenadas)


def test_avl_rotacoes():
    tree = AVL()
    for i in range(1, 8):
        consulta = Consulta(i, f"Cliente_{i}", Intervalo(i * 2, i * 2 + 1))
        assert tree.inserir(consulta)
        assert is_valid_avl(tree)
    assert tree.altura() == 2


def test_rb_propriedades_de_cor():
    tree = RedBlackTree()
    for i in range(1, 15):
        consulta = Consulta(i, f"Cliente_{i}", Intervalo(i * 2, i * 2 + 1))
        assert tree.inserir(consulta)
        assert is_valid_rb(tree)
