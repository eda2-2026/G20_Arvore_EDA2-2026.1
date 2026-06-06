import pytest
from models import Consulta, Intervalo
from trees import AVL, RedBlackTree

@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_buscar_todos_conflitos_retorna_multiplos(tree_class):
    tree = tree_class()
    consultas = [
        Consulta(1, "A", Intervalo(10, 15)),
        Consulta(2, "B", Intervalo(16, 20)),
        Consulta(3, "C", Intervalo(21, 25)),
        Consulta(4, "D", Intervalo(30, 40)),
    ]
    for c in consultas:
        tree.inserir(c)
        
    conflitos = tree.buscar_todos_conflitos(Intervalo(12, 23))
    # Deve conflitar com A (10-15), B (16-20) e C (21-25)
    assert len(conflitos) == 3
    ids = [c.id_consulta for c in conflitos]
    assert sorted(ids) == [1, 2, 3]

@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_buscar_todos_conflitos_sem_conflito(tree_class):
    tree = tree_class()
    tree.inserir(Consulta(1, "A", Intervalo(10, 20)))
    conflitos = tree.buscar_todos_conflitos(Intervalo(20, 30))
    assert len(conflitos) == 0

@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_buscar_por_intervalo_contido(tree_class):
    tree = tree_class()
    consultas = [
        Consulta(1, "A", Intervalo(10, 12)),
        Consulta(2, "B", Intervalo(13, 18)),
        Consulta(3, "C", Intervalo(19, 25)),
    ]
    for c in consultas:
        tree.inserir(c)
        
    # A (10-12) e B (13-18) estão totalmente contidos em [10, 19)
    contidos = tree.buscar_por_intervalo(10, 19)
    assert len(contidos) == 2
    ids = sorted([c.id_consulta for c in contidos])
    assert ids == [1, 2]
    
    # A, B, C estão contidos em [5, 25)
    contidos2 = tree.buscar_por_intervalo(5, 25)
    assert len(contidos2) == 3

@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_buscar_por_intervalo_vazio(tree_class):
    tree = tree_class()
    assert len(tree.buscar_por_intervalo(0, 100)) == 0

@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_tamanho_apos_insercoes_e_remocoes(tree_class):
    tree = tree_class()
    assert tree.tamanho() == 0
    
    c1 = Consulta(1, "A", Intervalo(1, 2))
    c2 = Consulta(2, "B", Intervalo(2, 3))
    
    tree.inserir(c1)
    tree.inserir(c2)
    assert tree.tamanho() == 2
    
    tree.remover(c1)
    assert tree.tamanho() == 1

@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_verificar_integridade_valida(tree_class):
    tree = tree_class()
    for i in range(10):
        tree.inserir(Consulta(i, str(i), Intervalo(i, i+5)))
    assert tree.verificar_integridade() is True

@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_verificar_integridade_apos_remocoes(tree_class):
    tree = tree_class()
    consultas = [Consulta(i, str(i), Intervalo(i*2, i*2+3)) for i in range(15)]
    for c in consultas:
        tree.inserir(c)
        
    # Remove alguns
    tree.remover(consultas[0])
    tree.remover(consultas[7])
    tree.remover(consultas[14])
    
    assert tree.verificar_integridade() is True

@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_max_end_correto_apos_remocao(tree_class):
    tree = tree_class()
    c1 = Consulta(1, "A", Intervalo(10, 15))
    c2 = Consulta(2, "B", Intervalo(5, 8))
    c3 = Consulta(3, "C", Intervalo(16, 25))
    
    tree.inserir(c1)
    tree.inserir(c2)
    tree.inserir(c3)
    
    # max_end global deve ser 25 (de c3)
    assert tree.raiz.max_end == 25
    
    # Remove c3
    tree.remover(c3)
    
    # max_end agora deve ser 15 (de c1)
    assert tree.raiz.max_end == 15
    assert tree.verificar_integridade() is True

def test_inserir_intervalo_invalido():
    with pytest.raises(ValueError):
        Consulta(1, "A", Intervalo(20, 10))

@pytest.mark.parametrize("tree_class", [AVL, RedBlackTree])
def test_remocao_elemento_inexistente(tree_class):
    tree = tree_class()
    c1 = Consulta(1, "A", Intervalo(10, 20))
    tree.inserir(c1)
    
    c2 = Consulta(2, "B", Intervalo(50, 60))
    assert tree.remover(c2) is False
    assert tree.tamanho() == 1
