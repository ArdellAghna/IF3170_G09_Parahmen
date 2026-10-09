import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"

# Buat direktori output
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Parameter Eksperimen Dasar (selain GA) - Wajib run 3 kali sesuai spek
NUM_RUNS_STANDARD = 3

# Parameter Eksperimen GA sesuai spesifikasi
# 1. Jumlah populasi sebagai kontrol (variasi iterasi)
GA_CONST_POPULATION = 20
GA_ITERATION_VARS = [50, 100, 150]

# 2. Banyak iterasi sebagai kontrol (variasi populasi)
GA_CONST_ITERATIONS = 100
GA_POPULATION_VARS = [10, 20, 30]
