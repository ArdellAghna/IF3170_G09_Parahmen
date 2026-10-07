from __future__ import annotations

from src.objective import feasible_value, objective

from tests.helper import make_package, make_state, make_truck


class TestObjective:
    def test_objective_jumlah_value(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=2, l=2, h=2, value=10, position=(0, 0, 0))
        b = make_package("b", w=2, l=2, h=2, value=20, position=(2, 0, 0))
        state = make_state(truck, [a, b])
        assert objective(state) == 30

    def test_objective_hanya_paket_di_dalam(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=2, l=2, h=2, value=10, position=(0, 0, 0))
        b = make_package("b", w=2, l=2, h=2, value=999, position=None)
        state = make_state(truck, [a, b])
        assert objective(state) == 10
        assert feasible_value(state) == 10

    def test_objective_negatif_bila_infeasible(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=2, l=2, h=2, value=10, position=(9, 9, 9))
        state = make_state(truck, [a])
        assert objective(state) < 0