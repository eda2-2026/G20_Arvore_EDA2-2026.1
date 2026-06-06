from typing import Optional, List
from models import Intervalo, Consulta
from .node import Node

class AVL:
    def __init__(self):
        self.raiz: Optional[Node] = None
        self.rotacoes: int = 0  # Contador de rotações para benchmark

    def obter_altura(self, nodo: Optional[Node]) -> int:
        if nodo is None:
            return 0
        return nodo.altura

    def obter_fator_balanceamento(self, nodo: Optional[Node]) -> int:
        if nodo is None:
            return 0
        return self.obter_altura(nodo.esquerda) - self.obter_altura(nodo.direita)

    def atualizar_max_end(self, nodo: Node) -> None:
        if nodo is None:
            return
        val_esq = nodo.esquerda.max_end if nodo.esquerda else 0
        val_dir = nodo.direita.max_end if nodo.direita else 0
        nodo.max_end = max(nodo.intervalo.fim, val_esq, val_dir)

    def rotacionar_direita(self, y: Node) -> Node:
        r"""
            y
           / \
          x   T3       ==>        x
         / \                     / \
        T1  T2                  T1  y
                                   / \
                                  T2  T3
        """
        x = y.esquerda
        assert x is not None
        T2 = x.direita

        # Rotação
        x.direita = y
        y.esquerda = T2

        # Ajuste de pais
        x.pai = y.pai
        y.pai = x
        if T2 is not None:
            T2.pai = y

        # Atualiza alturas
        y.altura = 1 + max(self.obter_altura(y.esquerda), self.obter_altura(y.direita))
        self.atualizar_max_end(y)

        x.altura = 1 + max(self.obter_altura(x.esquerda), self.obter_altura(x.direita))
        self.atualizar_max_end(x)

        self.rotacoes += 1
        return x

    def rotacionar_esquerda(self, x: Node) -> Node:
        r"""
          x                       y
         / \                     / \
        T1  y        ==>        x   T3
           / \                 / \
          T2  T3              T1  T2
        """
        y = x.direita
        assert y is not None
        T2 = y.esquerda

        # Rotação
        y.esquerda = x
        x.direita = T2

        # Ajuste de pais
        y.pai = x.pai
        x.pai = y
        if T2 is not None:
            T2.pai = x

        # Atualiza alturas
        x.altura = 1 + max(self.obter_altura(x.esquerda), self.obter_altura(x.direita))
        self.atualizar_max_end(x)

        y.altura = 1 + max(self.obter_altura(y.esquerda), self.obter_altura(y.direita))
        self.atualizar_max_end(y)

        self.rotacoes += 1
        return y

    def buscar_conflito(self, intervalo: Intervalo) -> Optional[Consulta]:
        """Busca se existe alguma consulta já registrada que conflite com o intervalo dado."""
        return self._buscar_conflito_recursivo(self.raiz, intervalo)

    def _buscar_conflito_recursivo(self, nodo: Optional[Node], intervalo: Intervalo) -> Optional[Consulta]:
        if nodo is None:
            return None

        # 1. Se o intervalo do nó atual conflita, retorna a consulta
        if nodo.intervalo.sobrepoe(intervalo):
            return nodo.consulta

        # 2. Se o filho esquerdo existe e seu max_end é maior que o início do intervalo buscado,
        # significa que pode haver um conflito na subárvore esquerda.
        if nodo.esquerda is not None and nodo.esquerda.max_end > intervalo.inicio:
            conflito_esq = self._buscar_conflito_recursivo(nodo.esquerda, intervalo)
            if conflito_esq is not None:
                return conflito_esq

        # 3. Caso contrário, ou se não achou na esquerda, procura na direita.
        return self._buscar_conflito_recursivo(nodo.direita, intervalo)

    def inserir(self, consulta: Consulta) -> bool:
        """Tenta inserir um agendamento. Retorna True se inserido com sucesso, 
        ou False se houver conflito de horário."""
        if self.buscar_conflito(consulta.intervalo) is not None:
            return False
        self.raiz = self._inserir_recursivo(self.raiz, consulta)
        if self.raiz is not None:
            self.raiz.pai = None
        return True

    def _inserir_recursivo(self, nodo: Optional[Node], consulta: Consulta) -> Node:
        if nodo is None:
            return Node(consulta)

        # Ordena pela chave primária: início do intervalo
        if consulta.intervalo.inicio < nodo.intervalo.inicio:
            nodo.esquerda = self._inserir_recursivo(nodo.esquerda, consulta)
            nodo.esquerda.pai = nodo
        else:
            nodo.direita = self._inserir_recursivo(nodo.direita, consulta)
            nodo.direita.pai = nodo

        # Atualiza altura e max_end do nó atual
        nodo.altura = 1 + max(self.obter_altura(nodo.esquerda), self.obter_altura(nodo.direita))
        self.atualizar_max_end(nodo)

        # Fator de balanceamento para verificar se desbalanceou
        fb = self.obter_fator_balanceamento(nodo)

        # Caso 1: Esquerda-Esquerda
        if fb > 1 and consulta.intervalo.inicio < nodo.esquerda.intervalo.inicio:
            return self.rotacionar_direita(nodo)

        # Caso 2: Direita-Direita
        if fb < -1 and consulta.intervalo.inicio >= nodo.direita.intervalo.inicio:
            return self.rotacionar_esquerda(nodo)

        # Caso 3: Esquerda-Direita
        if fb > 1 and consulta.intervalo.inicio >= nodo.esquerda.intervalo.inicio:
            nodo.esquerda = self.rotacionar_esquerda(nodo.esquerda)
            return self.rotacionar_direita(nodo)

        # Caso 4: Direita-Esquerda
        if fb < -1 and consulta.intervalo.inicio < nodo.direita.intervalo.inicio:
            nodo.direita = self.rotacionar_direita(nodo.direita)
            return self.rotacionar_esquerda(nodo)

        return nodo

    def remover(self, consulta: Consulta) -> bool:
        """Remove um agendamento específico. Retorna True se removido, False caso contrário."""
        achado = self._buscar_por_id(self.raiz, consulta.intervalo.inicio, consulta.id_consulta)
        if achado is None:
            return False
        
        self.raiz = self._remover_recursivo(self.raiz, consulta.intervalo.inicio, consulta.id_consulta)
        if self.raiz is not None:
            self.raiz.pai = None
        return True

    def _buscar_por_id(self, nodo: Optional[Node], inicio: int, id_consulta: int) -> Optional[Node]:
        if nodo is None:
            return None
        if nodo.intervalo.inicio == inicio and nodo.consulta.id_consulta == id_consulta:
            return nodo
        
        if inicio < nodo.intervalo.inicio:
            return self._buscar_por_id(nodo.esquerda, inicio, id_consulta)
        elif inicio > nodo.intervalo.inicio:
            return self._buscar_por_id(nodo.direita, inicio, id_consulta)
        else:
            # Chaves iguais no início: busca em ambas as direções por garantia
            res_esq = self._buscar_por_id(nodo.esquerda, inicio, id_consulta)
            if res_esq is not None:
                return res_esq
            return self._buscar_por_id(nodo.direita, inicio, id_consulta)

    def _remover_recursivo(self, nodo: Optional[Node], inicio: int, id_consulta: int) -> Optional[Node]:
        if nodo is None:
            return None

        if inicio < nodo.intervalo.inicio:
            nodo.esquerda = self._remover_recursivo(nodo.esquerda, inicio, id_consulta)
            if nodo.esquerda is not None:
                nodo.esquerda.pai = nodo
        elif inicio > nodo.intervalo.inicio:
            nodo.direita = self._remover_recursivo(nodo.direita, inicio, id_consulta)
            if nodo.direita is not None:
                nodo.direita.pai = nodo
        else:
            # Encontrou nó com início igual
            if nodo.consulta.id_consulta == id_consulta:
                if nodo.esquerda is None:
                    return nodo.direita
                elif nodo.direita is None:
                    return nodo.esquerda

                sucessor = self._min_valor_nodo(nodo.direita)
                nodo.consulta = sucessor.consulta
                nodo.intervalo = sucessor.intervalo
                nodo.direita = self._remover_recursivo(nodo.direita, sucessor.intervalo.inicio, sucessor.consulta.id_consulta)
                if nodo.direita is not None:
                    nodo.direita.pai = nodo
            else:
                # Se início for idêntico mas ID diferente, busca em ambos os lados
                nodo.esquerda = self._remover_recursivo(nodo.esquerda, inicio, id_consulta)
                if nodo.esquerda is not None:
                    nodo.esquerda.pai = nodo
                nodo.direita = self._remover_recursivo(nodo.direita, inicio, id_consulta)
                if nodo.direita is not None:
                    nodo.direita.pai = nodo

        if nodo is None:
            return None

        # Atualiza altura e max_end do nó ancestral
        nodo.altura = 1 + max(self.obter_altura(nodo.esquerda), self.obter_altura(nodo.direita))
        self.atualizar_max_end(nodo)

        # Fator de balanceamento
        fb = self.obter_fator_balanceamento(nodo)

        # Caso 1: Esquerda-Esquerda
        if fb > 1 and self.obter_fator_balanceamento(nodo.esquerda) >= 0:
            return self.rotacionar_direita(nodo)

        # Caso 2: Esquerda-Direita
        if fb > 1 and self.obter_fator_balanceamento(nodo.esquerda) < 0:
            nodo.esquerda = self.rotacionar_esquerda(nodo.esquerda)
            return self.rotacionar_direita(nodo)

        # Caso 3: Direita-Direita
        if fb < -1 and self.obter_fator_balanceamento(nodo.direita) <= 0:
            return self.rotacionar_esquerda(nodo)

        # Caso 4: Direita-Esquerda
        if fb < -1 and self.obter_fator_balanceamento(nodo.direita) > 0:
            nodo.direita = self.rotacionar_direita(nodo.direita)
            return self.rotacionar_esquerda(nodo)

        return nodo

    def _min_valor_nodo(self, nodo: Node) -> Node:
        atual = nodo
        while atual.esquerda is not None:
            atual = atual.esquerda
        return atual

    def altura(self) -> int:
        if self.raiz is None:
            return -1
        return self.raiz.altura - 1

    def em_ordem(self) -> List[Consulta]:
        resultado: List[Consulta] = []
        self._em_ordem_recursivo(self.raiz, resultado)
        return resultado

    def _em_ordem_recursivo(self, nodo: Optional[Node], resultado: List[Consulta]) -> None:
        if nodo is not None:
            self._em_ordem_recursivo(nodo.esquerda, resultado)
            resultado.append(nodo.consulta)
            self._em_ordem_recursivo(nodo.direita, resultado)

    def buscar_todos_conflitos(self, intervalo: Intervalo) -> List[Consulta]:
        """Retorna todas as consultas que conflitam com o intervalo dado."""
        resultado: List[Consulta] = []
        self._buscar_todos_recursivo(self.raiz, intervalo, resultado)
        return resultado

    def _buscar_todos_recursivo(self, nodo: Optional[Node], intervalo: Intervalo, resultado: List[Consulta]) -> None:
        if nodo is None:
            return
        
        # Se max_end do filho esquerdo é maior que o início do intervalo, 
        # pode haver conflitos na subárvore esquerda
        if nodo.esquerda is not None and nodo.esquerda.max_end > intervalo.inicio:
            self._buscar_todos_recursivo(nodo.esquerda, intervalo, resultado)
            
        # Verifica nó atual
        if nodo.intervalo.sobrepoe(intervalo):
            resultado.append(nodo.consulta)
            
        # Verifica subárvore direita: apenas se o início do nó atual for menor que o fim do intervalo buscado,
        # pois a árvore é ordenada pelo início.
        if nodo.intervalo.inicio < intervalo.fim:
            self._buscar_todos_recursivo(nodo.direita, intervalo, resultado)

    def buscar_por_intervalo(self, inicio: int, fim: int) -> List[Consulta]:
        """Retorna todas as consultas cujo intervalo está inteiramente contido em [inicio, fim)."""
        resultado: List[Consulta] = []
        self._buscar_por_intervalo_recursivo(self.raiz, inicio, fim, resultado)
        return resultado

    def _buscar_por_intervalo_recursivo(self, nodo: Optional[Node], inicio: int, fim: int, resultado: List[Consulta]) -> None:
        if nodo is None:
            return
            
        # Como os nós são ordenados pelo inicio, se nodo.intervalo.inicio >= inicio,
        # ainda pode haver nós contidos à esquerda. Se < inicio, tudo à esquerda também será < inicio,
        # então não pode estar contido.
        if nodo.intervalo.inicio >= inicio:
            self._buscar_por_intervalo_recursivo(nodo.esquerda, inicio, fim, resultado)
            
        if nodo.intervalo.inicio >= inicio and nodo.intervalo.fim <= fim:
            resultado.append(nodo.consulta)
            
        if nodo.intervalo.inicio < fim:
            self._buscar_por_intervalo_recursivo(nodo.direita, inicio, fim, resultado)

    def tamanho(self) -> int:
        """Retorna o número de nós (consultas) na árvore."""
        return self._tamanho_recursivo(self.raiz)

    def _tamanho_recursivo(self, nodo: Optional[Node]) -> int:
        if nodo is None:
            return 0
        return 1 + self._tamanho_recursivo(nodo.esquerda) + self._tamanho_recursivo(nodo.direita)

    def verificar_integridade(self) -> bool:
        """Verifica se as propriedades da BST, AVL e max_end são mantidas."""
        return (self._verificar_bst(self.raiz, float('-inf'), float('inf')) and
                self._verificar_avl(self.raiz)[0] and
                self._verificar_max_end(self.raiz))

    def _verificar_bst(self, nodo: Optional[Node], min_val: float, max_val: float) -> bool:
        if nodo is None:
            return True
        chave = nodo.intervalo.inicio
        # Permite duplicatas à direita (<= e >=)
        if not (min_val <= chave <= max_val):
            return False
        return (self._verificar_bst(nodo.esquerda, min_val, chave) and
                self._verificar_bst(nodo.direita, chave, max_val))

    def _verificar_avl(self, nodo: Optional[Node]) -> tuple[bool, int]:
        if nodo is None:
            return True, 0
        ok_esq, alt_esq = self._verificar_avl(nodo.esquerda)
        ok_dir, alt_dir = self._verificar_avl(nodo.direita)
        
        if not ok_esq or not ok_dir:
            return False, 0
            
        if abs(alt_esq - alt_dir) > 1:
            return False, 0
            
        if nodo.altura != 1 + max(alt_esq, alt_dir):
            return False, 0
            
        return True, 1 + max(alt_esq, alt_dir)

    def _verificar_max_end(self, nodo: Optional[Node]) -> bool:
        if nodo is None:
            return True
            
        val_esq = nodo.esquerda.max_end if nodo.esquerda else 0
        val_dir = nodo.direita.max_end if nodo.direita else 0
        esperado = max(nodo.intervalo.fim, val_esq, val_dir)
        
        if nodo.max_end != esperado:
            return False
            
        return self._verificar_max_end(nodo.esquerda) and self._verificar_max_end(nodo.direita)
