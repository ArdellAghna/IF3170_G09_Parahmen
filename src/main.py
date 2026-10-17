import json
import random
from typing import List

from src.config import (
    OUTPUT_DIR, NUM_RUNS_STANDARD, RANDOM_SEED,
    GA_CONST_POPULATION, GA_ITERATION_VARS, 
    GA_CONST_ITERATIONS, GA_POPULATION_VARS
)
from src.init import random_initial_state
from src.model.package import Package
from src.model.truck import Truck
from src.algoritma import hill_climbing, simulated_annealing, genetic_algorithm

def generate_test_case() -> tuple[Truck, List[Package]]:
    random.seed(RANDOM_SEED)
    truck = Truck({"w": 20, "l": 40, "h": 20}, max_capacity=2000)
    packages = []
    # Buat 25 paket acak untuk eksperimen
    for i in range(25):
        w, l, h = random.randint(2, 6), random.randint(2, 6), random.randint(2, 6)
        val = random.randint(10, 100)
        weight = random.randint(5, 50)
        is_fragile = random.random() < 0.2
        packages.append(Package(f"PKG_{i}", {"w": w, "l": l, "h": h}, value=val, weight=weight, is_fragile=is_fragile))
    return truck, packages

def save_result(result, filename: str):
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2)

def run_all_experiments():
    rng = random.Random(RANDOM_SEED)
    truck, packages = generate_test_case()
    
    print("Membangkitkan initial state (ini mungkin memakan waktu sebentar)...")
    initial_state = random_initial_state(truck, packages, rng)
    print(f"Initial state berhasil dibuat! Total Value: {initial_state.value()}")

    # 1. Eksperimen Standard (HC & SA)
    print("\n--- Menjalankan Hill Climbing & Simulated Annealing ---")
    for i in range(NUM_RUNS_STANDARD):
        run_idx = i + 1
        print(f"> Run {run_idx}/{NUM_RUNS_STANDARD}...")
        
        # Hill Climbing (4 Varian)
        for variant in hill_climbing.VARIANTS:
            params = hill_climbing.HCParams(variant=variant, max_iterations=200)
            res = hill_climbing.run(initial_state, params, seed=rng.randint(0, 99999))
            save_result(res, f"hc_{variant}_run{run_idx}.json")
            print(f"  - HC {variant} selesai (Obj: {res.final_objective})")
            
        # Simulated Annealing
        sa_params = simulated_annealing.SAParams(max_iterations=1000)
        res_sa = simulated_annealing.run(initial_state, sa_params, seed=rng.randint(0, 99999))
        save_result(res_sa, f"sa_run{run_idx}.json")
        print(f"  - SA selesai (Obj: {res_sa.final_objective})")

    # 2. Eksperimen GA
    print("\n--- Menjalankan Genetic Algorithm ---")
    # a. Variasi Iterasi (Populasi konstan) -> Skenario A
    for max_gen in GA_ITERATION_VARS:
        for i in range(NUM_RUNS_STANDARD):
            run_idx = i + 1
            print(f"> GA A (Pop={GA_CONST_POPULATION}, Gen={max_gen}) Run {run_idx}...")
            ga_params = genetic_algorithm.GAParams(pop_size=GA_CONST_POPULATION, max_generations=max_gen)
            res_ga = genetic_algorithm.run(initial_state, ga_params, seed=rng.randint(0, 99999))
            save_result(res_ga, f"ga_A_pop{GA_CONST_POPULATION}_gen{max_gen}_run{run_idx}.json")

    # b. Variasi Populasi (Iterasi konstan) -> Skenario B
    for pop_size in GA_POPULATION_VARS:
        for i in range(NUM_RUNS_STANDARD):
            run_idx = i + 1
            print(f"> GA B (Pop={pop_size}, Gen={GA_CONST_ITERATIONS}) Run {run_idx}...")
            ga_params = genetic_algorithm.GAParams(pop_size=pop_size, max_generations=GA_CONST_ITERATIONS)
            res_ga = genetic_algorithm.run(initial_state, ga_params, seed=rng.randint(0, 99999))
            save_result(res_ga, f"ga_B_pop{pop_size}_gen{GA_CONST_ITERATIONS}_run{run_idx}.json")

    print("\n SEMUA EKSPERIMEN SELESAI! Hasil run (.json) tersimpan di folder output/")

if __name__ == "__main__":
    run_all_experiments()
