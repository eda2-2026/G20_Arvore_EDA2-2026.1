from typing import Optional, List
from models import Intervalo, Consulta
from .trees.node import Node

class RedBlackTree:
    def __init__(self):
        # Criação do nó sentinela NIL (preto, folha fictícia)
        self.NIL = Node(None)
        self.NIL.color = False
        self.NIL.esquerda = self.NIL
        self.NIL.direita = self.NIL
        self.NIL.pai = self.NIL
        self.NIL.max_end = 0
        self.raiz: Node = self.NIL
        self.rotacoes: int = 0  # Contador de rotações para benchmark

    def atualizar_max_end(self, nodo: Node) -> None:
        if nodo is None or nodo == self.NIL:
            return
        val_esq = nodo.esquerda.max_end if nodo.esquerda != self.NIL else 0
        val_dir = nodo.direita.max_end if nodo.direita != self.NIL else 0
        nodo.max_end = max(nodo.intervalo.fim, val_esq, val_dir)

    def atualizar_caminho_ate_raiz(self, nodo: Node) -> None:
        curr = nodo
        while curr != self.NIL and curr is not None:
            self.atualizar_max_end(curr)
            curr = curr.pai

    def rotacionar_esquerda(self, x: Node) -> None:
        y = x.direita
        assert y is not None and y != self.NIL
        
        x.direita = y.esquerda
        if y.esquerda != self.NIL:
            y.esquerda.pai = x
            
        y.pai = x.pai
        if x.pai == self.NIL:
            self.raiz = y
        elif x == x.pai.esquerda:
            x.pai.esquerda = y
        else:
            x.pai.direita = y
            
        y.esquerda = x
        x.pai = y

        # Atualiza max_end: como x passa a ser filho de y, atualiza x primeiro
        self.atualizar_max_end(x)
        self.atualizar_max_end(y)
        self.rotacoes += 1

    def rotacionar_direita(self, y: Node) -> None:
        x = y.esquerda
        assert x is not None and x != self.NIL
        
        y.esquerda = x.direita
        if x.direita != self.NIL:
            x.direita.pai = y
            
        x.pai = y.pai
        if y.pai == self.NIL:
            self.raiz = x
        elif y == y.pai.esquerda:
            y.pai.esquerda = x
        else:
            y.pai.direita = x
            
        x.direita = y
        y.pai = x

        # Atualiza max_end: como y passa a ser filho de x, atualiza y primeiro
        self.atualizar_max_end(y)
        self.atualizar_max_end(x)
        self.rotacoes += 1

    def buscar_conflito(self, intervalo: Intervalo) -> Optional[Consulta]:
        """Busca se há conflitos com o intervalo fornecido."""
        return self._buscar_conflito_recursivo(self.raiz, intervalo)

    def _buscar_conflito_recursivo(self, nodo: Node, intervalo: Intervalo) -> Optional[Consulta]:
        if nodo == self.NIL or nodo is None:
            return None

        # 1. Verifica se o nó atual se sobrepõe
        if nodo.intervalo.sobrepoe(intervalo):
            return nodo.consulta

        # 2. Se o filho esquerdo existe e seu max_end > inicio do intervalo, entra na esquerda
        if nodo.esquerda != self.NIL and nodo.esquerda.max_end > intervalo.inicio:
            conflito_esq = self._buscar_conflito_recursivo(nodo.esquerda, intervalo)
            if conflito_esq is not None:
                return conflito_esq

        # 3. Caso contrário, ou se não achou conflito na esquerda, busca na direita
        return self._buscar_conflito_recursivo(nodo.direita, intervalo)

    def inserir(self, consulta: Consulta) -> bool:
        """Insere um agendamento na árvore. Retorna True se inserido, False se houver conflito."""
        if self.buscar_conflito(consulta.intervalo) is not None:
            return False

        nodo = Node(consulta)
        nodo.color = True  # Novos nós são sempre vermelhos
        nodo.esquerda = self.NIL
        nodo.direita = self.NIL
        nodo.max_end = consulta.intervalo.fim

        y = self.NIL
        x = self.raiz
        while x != self.NIL:
            y = x
            if nodo.intervalo.inicio < x.intervalo.inicio:
                x = x.esquerda
            else:
                x = x.direita

        nodo.pai = y
        if y == self.NIL:
            self.raiz = nodo
        elif nodo.intervalo.inicio < y.intervalo.inicio:
            y.esquerda = nodo
        else:
            y.direita = nodo

        # Caminha de volta à raiz atualizando max_end antes do balanceamento
        self.atualizar_caminho_ate_raiz(nodo)

        if nodo.pai == self.NIL:
            nodo.color = False  # Raiz é preta
            return True

        if nodo.pai.pai == self.NIL:
            return True

        self._inserir_fixup(nodo)
        return True

    def _inserir_fixup(self, z: Node) -> None:
        while z.pai.color is True:  # Enquanto o pai for vermelho
            if z.pai == z.pai.pai.esquerda:
                y = z.pai.pai.direita  # tio de z
                if y.color is True:  # Caso 1: Tio é vermelho
                    z.pai.color = False
                    y.color = False
                    z.pai.pai.color = True
                    self.atualizar_max_end(z.pai)
                    self.atualizar_max_end(y)
                    self.atualizar_max_end(z.pai.pai)
                    z = z.pai.pai
                else:  # Caso 2 ou 3: Tio é preto
                    if z == z.pai.direita:  # Caso 2
                        z = z.pai
                        self.rotacionar_esquerda(z)
                    # Caso 3
                    z.pai.color = False
                    z.pai.pai.color = True
                    self.rotacionar_direita(z.pai.pai)
            else:
                y = z.pai.pai.esquerda  # tio de z
                if y.color is True:  # Caso 1
                    z.pai.color = False
                    y.color = False
                    z.pai.pai.color = True
                    self.atualizar_max_end(z.pai)
                    self.atualizar_max_end(y)
                    self.atualizar_max_end(z.pai.pai)
                    z = z.pai.pai
                else:  # Caso 2 ou 3
                    if z == z.pai.esquerda:  # Caso 2
                        z = z.pai
                        self.rotacionar_direita(z)
                    # Caso 3
                    z.pai.color = False
                    z.pai.pai.color = True
                    self.rotacionar_esquerda(z.pai.pai)
            if z == self.raiz:
                break
        self.raiz.color = False  # Raiz permanece preta

    def transplante(self, u: Node, v: Node) -> None:
        if u.pai == self.NIL:
            self.raiz = v
        elif u == u.pai.esquerda:
            u.pai.esquerda = v
        else:
            u.pai.direita = v
        v.pai = u.pai

    def remover(self, consulta: Consulta) -> bool:
        """Remove o agendamento fornecido da árvore. Retorna True se removido, False caso contrário."""
        z = self._buscar_nodo_especifico(consulta.intervalo.inicio, consulta.id_consulta)
        if z == self.NIL:
            return False

        y = z
        y_cor_original = y.color
        if z.esquerda == self.NIL:
            x = z.direita
            self.transplante(z, z.direita)
            start_update = x if x != self.NIL else z.pai
        elif z.direita == self.NIL:
            x = z.esquerda
            self.transplante(z, z.esquerda)
            start_update = x if x != self.NIL else z.pai
        else:
            y = self._min_valor_nodo(z.direita)
            y_cor_original = y.color
            x = y.direita
            if y.pai == z:
                x.pai = y
                start_update = y
            else:
                old_y_pai = y.pai
                self.transplante(y, y.direita)
                self.atualizar_caminho_ate_raiz(old_y_pai)
                y.direita = z.direita
                y.direita.pai = y
                start_update = y

            self.transplante(z, y)
            y.esquerda = z.esquerda
            y.esquerda.pai = y
            y.color = z.color

        self.atualizar_caminho_ate_raiz(start_update)

        if y_cor_original is False:
            self._remover_fixup(x)

        return True

    def _buscar_nodo_especifico(self, inicio: int, id_consulta: int) -> Node:
        return self._buscar_nodo_especifico_recursivo(self.raiz, inicio, id_consulta)

    def _buscar_nodo_especifico_recursivo(self, nodo: Node, inicio: int, id_consulta: int) -> Node:
        if nodo == self.NIL or nodo is None:
            return self.NIL

        if nodo.intervalo.inicio == inicio and nodo.consulta.id_consulta == id_consulta:
            return nodo

        res = self.NIL
        if inicio <= nodo.intervalo.inicio:
            res = self._buscar_nodo_especifico_recursivo(nodo.esquerda, inicio, id_consulta)
        if res == self.NIL and inicio >= nodo.intervalo.inicio:
            res = self._buscar_nodo_especifico_recursivo(nodo.direita, inicio, id_consulta)
        return res

    def _remover_fixup(self, x: Node) -> None:
        while x != self.raiz and x.color is False:
            if x == x.pai.esquerda:
                w = x.pai.direita  # irmão de x
                if w.color is True:  # Caso 1
                    w.color = False
                    x.pai.color = True
                    self.rotacionar_esquerda(x.pai)
                    w = x.pai.direita
                # Caso 2
                if w.esquerda.color is False and w.direita.color is False:
                    w.color = True
                    x = x.pai
                else:
                    # Caso 3
                    if w.direita.color is False:
                        w.esquerda.color = False
                        w.color = True
                        self.rotacionar_direita(w)
                        w = x.pai.direita
                    # Caso 4
                    w.color = x.pai.color
                    x.pai.color = False
                    w.direita.color = False
                    self.rotacionar_esquerda(x.pai)
                    x = self.raiz
            else:
                w = x.pai.esquerda  # irmão de x
                if w.color is True:  # Caso 1
                    w.color = False
                    x.pai.color = True
                    self.rotacionar_direita(x.pai)
                    w = x.pai.esquerda
                # Caso 2
                if w.direita.color is False and w.esquerda.color is False:
                    w.color = True
                    x = x.pai
                else:
                    # Caso 3
                    if w.esquerda.color is False:
                        w.direita.color = False
                        w.color = True
                        self.rotacionar_esquerda(w)
                        w = x.pai.esquerda
                    # Caso 4
                    w.color = x.pai.color
                    x.pai.color = False
                    w.esquerda.color = False
                    self.rotacionar_direita(x.pai)
                    x = self.raiz
        x.color = False

    def _min_valor_nodo(self, nodo: Node) -> Node:
        atual = nodo
        while atual.esquerda != self.NIL and atual.esquerda is not None:
            atual = atual.esquerda
        return atual

    def altura(self) -> int:
        return self._altura_recursiva(self.raiz)

    def _altura_recursiva(self, nodo: Node) -> int:
        if nodo == self.NIL or nodo is None:
            return -1
        return 1 + max(self._altura_recursiva(nodo.esquerda), self._altura_recursiva(nodo.direita))

    def em_ordem(self) -> List[Consulta]:
        resultado: List[Consulta] = []
        self._em_ordem_recursivo(self.raiz, resultado)
        return resultado

    def _em_ordem_recursivo(self, nodo: Node, resultado: List[Consulta]) -> None:
        if nodo != self.NIL and nodo is not None:
            self._em_ordem_recursivo(nodo.esquerda, resultado)
            resultado.append(nodo.consulta)
            self._em_ordem_recursivo(nodo.direita, resultado)
