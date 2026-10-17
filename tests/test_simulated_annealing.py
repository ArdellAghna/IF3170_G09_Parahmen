from __future__ import annotations

import random

from src.algoritma.simulated_annealing import SAParams, run
from src.constraints import check_feasible
from src.init import random_initial_state

from tests.helper import make_package, make_truck


def _build_case(n_pkgs: int = 5):
    truck = make_truck(w=12, l=12, h=8, max_cap=50)
    packages = [
        make_package(f"p{i}", w=2, l=2, h=2, value=10 + i, weight=1, is_fragile=(i % 5 == 0))
        for i in range(n_pkgs)
    ]
    return truck, packages


class TestSimulatedAnnealing:
    def test_metrik_konsisten_dengan_iterasi(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(3))
        res = run(state, SAParams(max_iterations=200, n_neighbors=3), seed=7)

        m = res.metrics
        total = (
            m["improving_moves"]
            + m["accepted_equal"]
            + m["accepted_worse"]
            + m["rejected"]
        )
        assert total == res.n_iterations
        assert len(m["prob_history"]) == res.n_iterations
        assert m["stuck_count"] <= res.n_iterations

    def test_state_akhir_feasible_dan_objective_tidak_menurun(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(5))
        res = run(state, SAParams(max_iterations=300, n_neighbors=3), seed=11)

        ok, violations = check_feasible(res.final_state)
        assert ok is True, f"state akhir infeasible: {violations}"
        assert res.final_objective >= res.initial_objective

    def test_berhenti_karena_jadwal_atau_batas_iterasi(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(9))
        params = SAParams(max_iterations=150, n_neighbors=3, cooling_rate=0.9)
        res = run(state, params, seed=13)

        berhenti_karena_suhu = res.metrics["final_temp"] <= params.temp_min
        berhenti_karena_batas = res.n_iterations == params.max_iterations
        berhenti_karena_tetangga_kosong = res.metrics["no_neighbor_steps"] > 0
        assert berhenti_karena_suhu or berhenti_karena_batas or berhenti_karena_tetangga_kosong

    def test_metrik_accepted_equal_terpisah(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(21))
        res = run(state, SAParams(max_iterations=100, n_neighbors=3), seed=2)

        assert "accepted_equal" in res.metrics
        assert "accepted_worse" in res.metrics
        assert "no_neighbor_steps" in res.metrics
