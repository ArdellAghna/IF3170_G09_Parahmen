from __future__ import annotations

import random

from src.algoritma import hill_climbing
from src.algoritma.hill_climbing import HCParams, VARIANTS, run
from src.config import RANDOM_SEED
from src.constraints import check_feasible
from src.init import random_initial_state
from src.model.result import Result
from src.moves import neighbor_states
from src.objective import objective

from tests.helper import make_package, make_state, make_truck


def _build_case(n_pkgs=6):
    truck = make_truck(w=20, l=20, h=10, max_cap=20)
    packages = [
        make_package(f"p{i}", w=(i % 3) + 1, l=((i + 1) % 3) + 1, h=((i + 2) % 2) + 1,
                     value=10 + i, weight=1, is_fragile=(i % 4 == 0), eta=i)
        for i in range(n_pkgs)
    ]
    return truck, packages


class TestRandomInitialState:
    def test_initial_state_feasible(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(RANDOM_SEED))
        feasible, violations = check_feasible(state)
        assert feasible is True, f"violations: {violations}"

    def test_initial_state_reproducible_dengan_seed(self):
        truck, packages = _build_case()
        s1 = random_initial_state(truck, packages, random.Random(7))
        s2 = random_initial_state(truck, packages, random.Random(7))
        assert s1.placements == s2.placements
        assert objective(s1) == objective(s2)

    def test_initial_state_tidak_mengubah_paket_asli(self):
        truck, packages = _build_case()
        originals = [p.position for p in packages]
        state = random_initial_state(truck, packages, random.Random(1))
        assert [p.position for p in packages] == originals
        assert state.total_weight() <= truck.max_cap


class TestNeighborStates:
    def test_neighbors_semua_feasible(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(3))
        nbrs = neighbor_states(state, random.Random(5), n_neighbors=25)
        assert len(nbrs) > 0
        for nb in nbrs:
            ok, viol = check_feasible(nb)
            assert ok is True, f"neighbor infeasible: {viol}"

    def test_neighbors_tidak_merusak_state_asal(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(3))
        before = dict(state.placements)
        neighbor_states(state, random.Random(5), n_neighbors=15)
        assert state.placements == before


class TestHillClimbing:
    def test_semua_varian_berjalan(self):
        truck, packages = _build_case()
        for variant in VARIANTS:
            state = random_initial_state(truck, packages, random.Random(11))
            params = HCParams(
                variant=variant,
                max_iterations=15,
                n_neighbors=20,
                max_sideways=5,
                max_restart=2,
            )
            res = run(state, params, seed=99)
            assert isinstance(res, Result)
            assert res.algorithm == "hill_climbing"
            assert res.variant == variant
            assert res.final_state is not None
            ok, viol = check_feasible(res.final_state)
            assert ok is True, f"[{variant}] state akhir infeasible: {viol}"

    def test_objective_tidak_menurun(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(2))
        for variant in VARIANTS:
            res = run(state, HCParams(variant=variant, max_iterations=12, n_neighbors=20), seed=1)
            assert res.final_objective >= res.initial_objective, variant

    def test_histori_terisi_dan_naik_tidak_menurun(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(4))
        res = run(state, HCParams(variant="steepest", max_iterations=10, n_neighbors=20), seed=8)
        assert len(res.history) >= 1
        for i in range(1, len(res.history)):
            assert res.history[i] >= res.history[i - 1] - 1e-9

    def test_hasil_durasi_dan_iterasi_tercatat(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(6))
        res = run(state, HCParams(variant="stochastic", max_iterations=10, n_neighbors=15), seed=3)
        assert res.duration > 0.0
        assert res.n_iterations >= 0
        assert "sideways_moves" in res.metrics
        assert "improving_moves" in res.metrics

    def test_restart_mencatat_jumlah_restart(self):
        truck, packages = _build_case()
        state = random_initial_state(truck, packages, random.Random(9))
        res = run(
            state,
            HCParams(variant="restart", max_iterations=5, n_neighbors=10, max_restart=2,
                     iterations_per_restart=5),
            seed=13,
        )
        assert res.metrics["restarts"] == 2
        assert len(res.metrics["iterations_per_restart"]) == 3  # 1 segmen awal + 2 restart


class TestSidewaysStop:
    def test_sideways_berhenti_saat_batas_tercapai(self):
        truck = make_truck(w=10, l=10, h=10, max_cap=100)
        a = make_package("a", w=1, l=1, h=1, value=10, position=(0, 0, 0))
        b = make_package("b", w=1, l=1, h=1, value=10, position=(2, 0, 0))
        state = make_state(truck, [a, b])

        plateau = [
            nb for nb in neighbor_states(state, random.Random(1), n_neighbors=20)
            if objective(nb) == objective(state)
        ]
        assert plateau, "prasyarat test: harus ada tetangga bernilai sama"

        res = run(
            state,
            HCParams(variant="sideways", max_iterations=50, n_neighbors=20, max_sideways=1),
            seed=1,
        )
        assert res.metrics["sideways_moves"] == 1
        assert res.n_iterations <= 2, "sideways harus berhenti saat batas tercapai"
        assert res.final_objective >= res.initial_objective


class TestVariantFunctions:
    def test_setiap_varian_punya_fungsi_sendiri(self):
        for nama in ("_steepest_ascent", "_sideways_move", "_stochastic", "_random_restart"):
            assert callable(getattr(hill_climbing, nama)), nama

    def test_dispatch_varian_mengembalikan_variant_sesuai(self):
        truck = make_truck(w=10, l=10, h=10, max_cap=100)
        pkg = make_package("a", w=1, l=1, h=1, value=10, position=(0, 0, 0))
        state = make_state(truck, [pkg])
        for variant in VARIANTS:
            res = run(state, HCParams(variant=variant, max_iterations=3, n_neighbors=5), seed=1)
            assert res.variant == variant
