from __future__ import annotations

import random

from src.algoritma.genetic_algorithm import GAParams, run
from src.constraints import check_feasible
from src.init import random_initial_state

from tests.helper import make_package, make_truck


def _build_case(n_pkgs: int = 6):
    truck = make_truck(w=14, l=14, h=8, max_cap=50)
    packages = [
        make_package(f"p{i}", w=(i % 3) + 1, l=((i + 1) % 3) + 1, h=((i + 2) % 2) + 1,
                     value=10 + i, weight=1, is_fragile=(i % 4 == 0))
        for i in range(n_pkgs)
    ]
    return truck, packages


class TestGeneticAlgorithm:
    def test_run_dasar(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(3))
        res = run(state, GAParams(pop_size=6, max_generations=5), seed=1)

        assert res.algorithm == "genetic_algorithm"
        assert res.n_iterations == 5
        assert len(res.history) == res.n_iterations + 1
        assert len(res.metrics["avg_history"]) == len(res.history)
        assert res.metrics["improving_generations"] >= 0

    def test_state_akhir_feasible(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(5))
        res = run(state, GAParams(pop_size=8, max_generations=6), seed=2)

        ok, violations = check_feasible(res.final_state)
        assert ok is True, f"state akhir infeasible: {violations}"

    def test_elitisme_menjaga_objective_terbaik(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(7))
        res = run(state, GAParams(pop_size=8, max_generations=8, elitism=2), seed=3)

        for i in range(1, len(res.history)):
            assert res.history[i] >= res.history[i - 1] - 1e-9
        assert res.final_objective >= res.initial_objective

    def test_parameter_tercatat(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(11))
        res = run(state, GAParams(pop_size=10, max_generations=4, mutation_rate=0.2), seed=4)

        assert res.params["pop_size"] == 10
        assert res.params["max_generations"] == 4
        assert res.params["mutation_rate"] == 0.2
