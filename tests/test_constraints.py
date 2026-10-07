from __future__ import annotations

import pytest

from src.constraints import (
    boxes_overlap,
    capacity_ok,
    check_feasible,
    fragile_supports,
    has_support,
    in_bounds,
    supporting_packages,
)
from src.model.state import State

from tests.helper import make_package, make_state, make_truck


class TestBounds:
    def test_package_sepenuhnya_dalam_truk(self):
        truck = make_truck(w=10, l=10, h=10)
        pkg = make_package("a", w=2, l=3, h=4, position=(1, 2, 3))
        assert in_bounds(pkg, truck) is True

    def test_paket_menembus_dinding_x(self):
        truck = make_truck(w=10, l=10, h=10)
        pkg = make_package("a", w=2, l=3, h=4, position=(9, 0, 0))  # x+w = 11 > 10
        assert in_bounds(pkg, truck) is False

    def test_paket_menembus_langit_langit(self):
        truck = make_truck(w=10, l=10, h=10)
        pkg = make_package("a", w=2, l=3, h=4, position=(0, 0, 8))  # z+h = 12 > 10
        assert in_bounds(pkg, truck) is False

    def test_paket_koordinat_negatif(self):
        truck = make_truck(w=10, l=10, h=10)
        pkg = make_package("a", w=2, l=3, h=4, position=(-1, 0, 0))
        assert in_bounds(pkg, truck) is False

    def test_check_feasible_deteksi_bounds(self):
        truck = make_truck(w=10, l=10, h=10)
        pkg = make_package("a", w=2, l=3, h=4, position=(9, 0, 0))
        state = make_state(truck, [pkg])
        feasible, violations = check_feasible(state)
        assert feasible is False
        assert any("C1_bounds" in v for v in violations)


class TestOverlap:
    def test_tumpang_tindih_2d(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=4, h=2, position=(0, 0, 0))
        b = make_package("b", w=4, l=4, h=2, position=(2, 2, 0))
        assert boxes_overlap(a, b) is True

    def test_samping_tidak_overlap(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=4, h=2, position=(0, 0, 0))
        b = make_package("b", w=4, l=4, h=2, position=(4, 0, 0))  # bersebelahan
        assert boxes_overlap(a, b) is False

    def test_bertumpuk_tidak_overlap(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=4, h=2, position=(0, 0, 0))
        b = make_package("b", w=4, l=4, h=2, position=(0, 0, 2))  # di atas a
        assert boxes_overlap(a, b) is False

    def test_check_feasible_deteksi_overlap(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=4, h=2, position=(0, 0, 0))
        b = make_package("b", w=4, l=4, h=2, position=(2, 2, 0))
        state = make_state(truck, [a, b])
        feasible, violations = check_feasible(state)
        assert feasible is False
        assert any("C5_overlap" in v for v in violations)


class TestSupport:
    def test_di_lantai_mempunyai_support(self):
        truck = make_truck(w=10, l=10, h=10)
        pkg = make_package("a", w=4, l=4, h=2, position=(0, 0, 0))
        assert has_support(pkg, [pkg], truck) is True

    def test_bertumpuk_valid_mempunyai_support(self):
        truck = make_truck(w=10, l=10, h=10)
        bawah = make_package("b", w=4, l=4, h=2, position=(0, 0, 0))
        atas = make_package("a", w=2, l=2, h=2, position=(1, 1, 2))
        assert has_support(atas, [bawah, atas], truck) is True
        assert supporting_packages(atas, [bawah, atas]) == [bawah]

    def test_melayang_tanpa_support(self):
        truck = make_truck(w=10, l=10, h=10)
        bawah = make_package("b", w=2, l=2, h=2, position=(0, 0, 0))
        atas = make_package("a", w=2, l=2, h=2, position=(8, 8, 2))  # tidak di atas bawah
        assert has_support(atas, [bawah, atas], truck) is False

    def test_melayang_di_ketinggian_tanpa_kolom(self):
        truck = make_truck(w=10, l=10, h=10)
        pkg = make_package("a", w=2, l=2, h=2, position=(3, 3, 5))  # kosong di bawahnya
        assert has_support(pkg, [pkg], truck) is False

    def test_support_parsial_tidak_melayang(self):
        truck = make_truck(w=10, l=10, h=10)
        bawah = make_package("b", w=2, l=2, h=2, position=(0, 0, 0))
        atas = make_package("a", w=4, l=4, h=2, position=(0, 0, 2))
        assert has_support(atas, [bawah, atas], truck) is True

    def test_kontak_sisi_bukan_support(self):
        truck = make_truck(w=10, l=10, h=10)
        b = make_package("b", w=2, l=2, h=2, position=(2, 2, 0))
        a = make_package("a", w=2, l=2, h=2, position=(2, 2, 2))
        # a tepat di atas b: b menjadi support a.
        assert has_support(a, [a, b], truck) is True
        # Sebaliknya b tetap di-support lantai, bukan oleh a.
        assert supporting_packages(b, [a, b]) == []


class TestFragile:
    def test_fragile_di_bawah_invalid(self):
        truck = make_truck(w=10, l=10, h=10)
        fragile = make_package("f", w=4, l=4, h=2, position=(0, 0, 0), is_fragile=True)
        normal = make_package("n", w=2, l=2, h=2, position=(1, 1, 2))
        state = make_state(truck, [fragile, normal])
        feasible, violations = check_feasible(state)
        assert feasible is False
        assert any("C3_fragile" in v for v in violations)
        assert fragile_supports(fragile, [fragile, normal]) == [normal]

    def test_fragile_di_atas_valid(self):
        truck = make_truck(w=10, l=10, h=10)
        normal = make_package("n", w=4, l=4, h=2, position=(0, 0, 0))
        fragile = make_package("f", w=2, l=2, h=2, position=(1, 1, 2), is_fragile=True)
        state = make_state(truck, [normal, fragile])
        feasible, _ = check_feasible(state)
        assert feasible is True


class TestCapacity:
    def test_over_capacity_invalid(self):
        truck = make_truck(w=10, l=10, h=10, max_cap=5)
        a = make_package("a", w=4, l=4, h=2, weight=3, position=(0, 0, 0))
        b = make_package("b", w=4, l=4, h=2, weight=3, position=(5, 0, 0))
        state = make_state(truck, [a, b])
        feasible, violations = check_feasible(state)
        assert feasible is False
        assert any("C4_capacity" in v for v in violations)
        assert capacity_ok(state) is False

    def test_pas_di_kapasitas_valid(self):
        truck = make_truck(w=10, l=10, h=10, max_cap=6)
        a = make_package("a", w=4, l=4, h=2, weight=3, position=(0, 0, 0))
        b = make_package("b", w=4, l=4, h=2, weight=3, position=(5, 0, 0))
        state = make_state(truck, [a, b])
        feasible, _ = check_feasible(state)
        assert feasible is True
        assert capacity_ok(state) is True


class TestStateFeasible:
    def test_state_kosong_feasible(self):
        truck = make_truck()
        state = make_state(truck, [])
        feasible, violations = check_feasible(state)
        assert feasible is True
        assert violations == []

    def test_paket_di_luar_truk_tidak_dihitung(self):
        truck = make_truck(w=10, l=10, h=10)
        luar = make_package("o", w=200, l=200, h=200)
        state = make_state(truck, [luar])
        feasible, violations = check_feasible(state)
        assert feasible is True
        assert violations == []