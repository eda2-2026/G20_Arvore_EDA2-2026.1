from dataclasses import dataclass

@dataclass
class Intervalo:
    inicio: int
    fim: int

    def __post_init__(self):
        if self.inicio >= self.fim:
            raise ValueError(f"Início ({self.inicio}) deve ser menor que o fim ({self.fim}).")

    def sobrepoe(self, outro: 'Intervalo') -> bool:
        # Define se há sobreposição considerando intervalos semi-abertos [inicio, fim)
        return self.inicio < outro.fim and outro.inicio < self.fim

    def __repr__(self) -> str:
        return f"[{self.inicio}, {self.fim})"

@dataclass
class Consulta:
    id_consulta: int
    cidadao: str
    intervalo: Intervalo

    def __repr__(self) -> str:
        return f"Consulta(id={self.id_consulta}, cidadao='{self.cidadao}', intervalo={self.intervalo})"
