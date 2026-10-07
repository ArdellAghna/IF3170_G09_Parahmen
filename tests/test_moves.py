from __future__ import annotations

import pytest

from src.model.package import VALID_ORIENTATIONS
from src.model.state import State
from src.moves import relocate, rotate_90, swap

from tests.helper import make_package, make_state, make_truck


def _assert_state_invariants(state: State):
    ids = [p.id for p in state.packages]
    assert len(ids) == len(set(ids)), "ID paket harus unik"
    for pkg in state.packages:
        # Orientasi harus valid.
        orient = tuple(pkg.orient[k] for k in ("w", "l", "h"))
        assert orient in VALID_ORIENTATIONS, f"orientasi tidak valid: {pkg.orient}"
        # Koordinat integer (bila di dalam truk).
        if pkg.position is not None:
            assert all(isinstance(c, int) for c in pkg.position), (
                f"koordinat harus integer: {pkg.position}"
            )


class TestSwap:
    def test_swap_menghasilkan_state_baru(self):
        truck = make_truck()
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0))
        b = make_package("b", w=2, l=2, h=2, position=(3, 3, 0))
        state = make_state(truck, [a, b])
        new_state = swap(state, "a", "b")
        assert new_state is not state

    def test_swap_tidak_mengubah_state_asal(self):
        truck = make_truck()
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0))
        b = make_package("b", w=2, l=2, h=2, position=(3, 3, 0))
        state = make_state(truck, [a, b])
        old_a = state.package_by_id("a").position
        old_b = state.package_by_id("b").position
        swap(state, "a", "b")
        assert state.package_by_id("a").position == old_a
        assert state.package_by_id("b").position == old_b

    def test_swap_posisi_posisi_tukar(self):
        truck = make_truck()
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0))
        b = make_package("b", w=2, l=2, h=2, position=(5, 5, 0))
        state = make_state(truck, [a, b])
        new_state = swap(state, "a", "b")
        assert new_state.package_by_id("a").position == (5, 5, 0)
        assert new_state.package_by_id("b").position == (0, 0, 0)

    def test_swap_keluar_masuk(self):
        truck = make_truck()
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0))
        b = make_package("b", w=2, l=2, h=2, position=None)
        state = make_state(truck, [a, b])
        new_state = swap(state, "a", "b")
        assert new_state.package_by_id("a").position is None
        assert new_state.package_by_id("b").position == (0, 0, 0)

    def test_swap_mempertahankan_invariants(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=2, l=3, h=4, position=(0, 0, 0))
        b = make_package("b", w=1, l=1, h=1, position=(5, 5, 0))
        state = make_state(truck, [a, b])
        new_state = swap(state, "a", "b")
        _assert_state_invariants(new_state)


class TestRelocate:
    def test_relocate_ke_posisi_baru(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0))
        state = make_state(truck, [a])
        new_state = relocate(state, "a", (3, 3, 0))
        assert new_state.package_by_id("a").position == (3, 3, 0)

    def test_relocate_keluar_truk(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0))
        state = make_state(truck, [a])
        new_state = relocate(state, "a", None)
        assert new_state.package_by_id("a").position is None

    def test_relocate_ke_tempat_sama_noop(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=2, l=2, h=2, position=(3, 3, 0))
        state = make_state(truck, [a])
        new_state = relocate(state, "a", (3, 3, 0))
        assert new_state.package_by_id("a").position == (3, 3, 0)
        assert new_state is not state  # tetap state baru, bukan identik

    def test_relocate_mempertahankan_invariants(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0))
        state = make_state(truck, [a])
        new_state = relocate(state, "a", (5, 5, 0))
        _assert_state_invariants(new_state)


class TestRotate:
    def test_rotasi_sumbu_z_tukar_w_l(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=2, h=3, position=(0, 0, 0))
        state = make_state(truck, [a])
        new_state = rotate_90(state, "a", "z")
        pkg_new = new_state.package_by_id("a")
        assert pkg_new.cur_dim == {"w": 2, "l": 4, "h": 3}

    def test_rotasi_sumbu_x_tukar_l_h(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=2, h=3, position=(0, 0, 0))
        state = make_state(truck, [a])
        new_state = rotate_90(state, "a", "x")
        pkg_new = new_state.package_by_id("a")
        assert pkg_new.cur_dim == {"w": 4, "l": 3, "h": 2}

    def test_rotasi_sumbu_y_tukar_w_h(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=2, h=3, position=(0, 0, 0))
        state = make_state(truck, [a])
        new_state = rotate_90(state, "a", "y")
        pkg_new = new_state.package_by_id("a")
        assert pkg_new.cur_dim == {"w": 3, "l": 2, "h": 4}

    def test_rotasi_enam_kemungkinan_orientasi(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=2, h=3, position=(0, 0, 0))
        orient_set = set()
        state = make_state(truck, [a])
        # Semua kemungkinan orientasi via kombinasi 0-3 rotasi.
        for r1 in ("", "x", "y", "z"):
            for r2 in ("", "x", "y", "z"):
                for r3 in ("", "x", "y", "z"):
                    s = state.copy()
                    for axis in (r1, r2, r3):
                        if axis:
                            s = rotate_90(s, "a", axis)
                    o = tuple(s.package_by_id("a").orient[k] for k in ("w", "l", "h"))
                    orient_set.add(o)
        assert len(orient_set) == 6

    def test_rotasi_mempertahankan_invariants(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=2, h=3, position=(0, 0, 0))
        state = make_state(truck, [a])
        new_state = rotate_90(state, "a", "x")
        _assert_state_invariants(new_state)

    def test_rotasi_tidak_mengubah_state_asal(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=2, h=3, position=(0, 0, 0))
        state = make_state(truck, [a])
        old_dims = dict(state.package_by_id("a").cur_dim)
        rotate_90(state, "a", "z")
        assert state.package_by_id("a").cur_dim == old_dims