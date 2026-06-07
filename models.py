from dataclasses import dataclass
from datetime import date, datetime, timedelta

BASE_DATE = date(2026, 1, 1)


def dias_para_data(dias: int) -> date:
    return BASE_DATE + timedelta(days=dias)


def format_ponto(ponto: int | date | datetime) -> str:
    if isinstance(ponto, int):
        return dias_para_data(ponto).isoformat()
    if isinstance(ponto, datetime):
        return ponto.date().isoformat()
    return ponto.isoformat()


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
        return f"[{format_ponto(self.inicio)}, {format_ponto(self.fim)})"

@dataclass
class Consulta:
    id_consulta: int
    cidadao: str
    intervalo: Intervalo

    def __repr__(self) -> str:
        return f"Consulta(id={self.id_consulta}, cidadao='{self.cidadao}', intervalo={self.intervalo})"
