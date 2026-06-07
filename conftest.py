import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path,
# permitindo que os testes importem `models`, `trees`, etc.
sys.path.insert(0, str(Path(__file__).resolve().parent))
