from typing import Optional
from models import Intervalo, Consulta

class Node:
    def __init__(self, consulta: Optional[Consulta] = None):
        self.consulta: Optional[Consulta] = consulta
        self.intervalo: Optional[Intervalo] = consulta.intervalo if consulta else None
        
        # O maior valor de término ('fim') em toda a subárvore deste nó
        self.max_end: int = self.intervalo.fim if self.intervalo else 0
        
        # Ponteiros da árvore
        self.esquerda: Optional['Node'] = None
        self.direita: Optional['Node'] = None
        self.pai: Optional['Node'] = None
        
        # Atributos de balanceamento
        self.altura: int = 1  # Usado para árvore AVL
        self.color: bool = True  # Usado para árvore Rubro-Negra (True = Vermelho, False = Preto)

    def __repr__(self) -> str:
        return f"Node(consulta={self.consulta}, max_end={self.max_end})"
