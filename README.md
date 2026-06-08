# Motor de Agendamento e Prevenção de Conflitos

**Estruturas de Dados e Algoritmos II — 2026.1 | Grupo G21**

Simulador que utiliza Árvores de Intervalos (baseadas em AVL e Rubro-Negra) para processar agendamentos do setor público e prevenir conflitos de horários em cenários de alta demanda.

## Demonstração Visual

[![Vídeo](https://img.youtube.com/vi/d8NUvTCBEn8/0.jpg)](https://youtu.be/d8NUvTCBEn8)

## Alunos
| Matrícula | Aluno |
| -- | -- |
| 241025990  | Pedro Henrique Ferreira Xavier |
| 241025247  | Gustavo Xavier Evangelista |

## Estrutura do Projeto

```
Motor_Agendamento_EDA2-2026.1/
├── main.py              # Ponto de entrada — cenários de agendamento e testes de estresse
├── models.py            # Classes Consulta e Intervalo (modelagem de dados)
├── utils.py             # Geração de dados sintéticos de tempo e validações
├── benchmark_chart.py   # Gerador de gráficos comparativos (Matplotlib)
├── graficos/            # Pasta com gráficos PNG e resultados em CSV das árvores
├── requirements.txt     # Dependências externas do projeto
├── tests/               # Suíte de testes automatizados de sobreposição (Pytest)
├── trees/               # Pacote de estruturas de dados (Árvores de Intervalos)
│   ├── __init__.py      # Re-exporta as estruturas
│   ├── node.py          # Nó base com campos de cor, altura e max_end
│   ├── avl.py           # Implementação da Árvore de Intervalos AVL
│   └── red_black.py     # Implementação da Árvore de Intervalos Rubro-Negra
├── LICENSE
└── README.md
```

## Como Executar

```bash
# Instalar as dependências (pytest, matplotlib)
pip install -r requirements.txt

# Executar todos os cenários com 10.000 agendamentos (padrão)
python main.py

# Especificar quantidade de consultas geradas
python main.py -n 50000

# Executar cenário de estresse específico
python main.py -c A          # Alta Escrita (Abertura de Agenda)
python main.py -c B          # Alta Leitura (Verificação de Disponibilidade)
python main.py -c C          # Fluxo Misto (Uso Real)

# Benchmark comparativo de rotações, tempo e altura
python main.py -c benchmark -n 50000

# Definir seed para reprodutibilidade dos horários gerados
python main.py -n 10000 -s 123

# Gerar gráficos de benchmark (Matplotlib) e exportar resultados para CSV
python benchmark_chart.py

# Ver os resultados do benchmark_chart
O script `benchmark_chart.py` gera os gráficos PNG e um relatório CSV na pasta `graficos/`.
- `graficos/benchmark_arvores_aleatorio.png`
- `graficos/benchmark_arvores_ordenado.png`
- `graficos/resultados_benchmark.csv`

# Executar a suíte de testes automatizados (validação rigorosa de conflitos)
pytest tests/

# Modo interativo de agenda
python main.py -c in
python main.py -c in --tree RB

## Cenários de Agendamento

| Cenário | Objetivo | Melhor Árvore Esperada | Dinâmica do Teste | Justificativa |
|---------|----------|------------------------|-------------------|---------------|
| **A — Alta Escrita** | Abertura de lote de vagas | Rubro-Negra (Red-Black) | 90% Inserções / 10% Buscas | Menos rotações exigidas no rebalanceamento durante inserções e remoções em massa. |
| **B — Alta Leitura** | Dia de pico de acessos | AVL | 10% Inserções / 90% Buscas | Balanceamento estrito garante altura mínima, otimizando o caminho de busca para achar lacunas. |
| **C — Fluxo Misto** | Operação diária normal | Empate Técnico | 50% Inserções / 50% Buscas | Avaliação do *trade-off* entre o custo de manter o balanceamento e a velocidade da consulta. |

## Estruturas Implementadas

Ambas as estruturas funcionam como **Árvores de Intervalos**, onde cada nó guarda um tempo de `início`, `fim` e o `max_end` (maior tempo de término detectado na respectiva subárvore).

| Estrutura | Complexidade Busca | Complexidade Inserção | Complexidade Remoção | Balanceamento | Arquivo |
|-----------|--------------------|-----------------------|----------------------|---------------|---------|
| Árvore AVL | O(log n) | O(log n) | O(log n) | Estrito (Fator Max Dif = 1) | `avl.py` |
| Árvore vermelho-preto | O(log n) | O(log n) | O(log n) | Flexível (Propriedades de Cores) | `red_black.py` |

## Requisitos

- Python 3.10+
- Pacotes externos: `pytest` (para testes unitários das lógicas de sobreposição) e `matplotlib` (para visualização e plotagem dos dados do benchmark).

## Licença

Consulte o arquivo [LICENSE](LICENSE).
