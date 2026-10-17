from __future__ import annotations

import pytest

from src.model.package import Package, VALID_ORIENTATIONS
from src.model.state import State
from src.model.truck import Truck

from tests.helper import make_package, make_state, make_truck


class TestPackage:
    def test_rotasi_kembali_ke_orientasi_asal(self):
        truck = make_truck()
        pkg = make_package("a", w=4, l=2, h=3)
        state = make_state(truck, [pkg])
        from src.moves import rotate_90

        for axis in ("z", "x", "y"):
            s = rotate_90(state.copy(), "a", axis)
            s = rotate_90(s, "a", axis)
            p = s.package_by_id("a")
            assert p.cur_dim == {"w": 4, "l": 2, "h": 3}, f"sumbu {axis}"

    def test_rotasi_satu_kali_mengubah_orientasi(self):
        from src.moves import rotate_90

        truck = make_truck()
        pkg = make_package("a", w=4, l=2, h=3)
        state = make_state(truck, [pkg])
        for axis in ("z", "x", "y"):
            s = rotate_90(state.copy(), "a", axis)
            p = s.package_by_id("a")
            assert p.cur_dim != {"w": 4, "l": 2, "h": 3}, f"sumbu {axis}"

    def test_enam_orientasi_valid(self):
        pkg = make_package("a", w=4, l=2, h=3)
        state = make_state(make_truck(), [pkg])
        from src.moves import rotate_90

        seen = set()
        for r1 in ("", "x", "y", "z"):
            for r2 in ("", "x", "y", "z"):
                for r3 in ("", "x", "y", "z"):
                    s = state.copy()
                    for axis in (r1, r2, r3):
                        if axis:
                            s = rotate_90(s, "a", axis)
                    o = tuple(s.package_by_id("a").orient[k] for k in ("w", "l", "h"))
                    seen.add(o)
        assert len(seen) == 6

    def test_set_orientation_valid(self):
        pkg = make_package("a", w=1, l=2, h=3)
        pkg.set_orientation({"w": "z", "l": "x", "h": "y"})
        assert pkg.cur_dim == {"w": 2, "l": 3, "h": 1}

    def test_set_orientation_invalid(self):
        pkg = make_package("a", w=1, l=2, h=3)
        with pytest.raises(ValueError):
            pkg.set_orientation({"w": "x", "l": "x", "h": "y"})

    def test_valid_orientations(self):
        assert len(VALID_ORIENTATIONS) == 6

    def test_package_copy_deep(self):
        pkg = make_package("a", w=1, l=2, h=3)
        c = pkg.copy()
        c.cur_dim["w"] = 999
        assert pkg.cur_dim["w"] != 999

    def test_package_to_dict_from_dict(self):
        pkg = make_package("a", w=1, l=2, h=3, position=(1, 2, 3), is_fragile=True, eta=4)
        d = pkg.to_dict()
        p2 = Package.from_dict(d)
        assert p2.id == pkg.id
        assert p2.og_dim == pkg.og_dim
        assert p2.cur_dim == pkg.cur_dim
        assert p2.orient == pkg.orient
        assert p2.position == pkg.position
        assert p2.is_fragile == pkg.is_fragile
        assert p2.eta == pkg.eta

    def test_package_to_dict_from_dict_setelah_rotasi(self):
        pkg = make_package("a", w=4, l=2, h=3)
        pkg.rotate("x")
        d = pkg.to_dict()
        p2 = Package.from_dict(d)
        assert p2.cur_dim == pkg.cur_dim
        assert p2.orient == pkg.orient


class TestTruck:
    def test_truck_to_dict_from_dict(self):
        t = make_truck(w=5, l=6, h=7, max_cap=8)
        d = t.to_dict()
        t2 = Truck.from_dict(d)
        assert t2.dim == t.dim
        assert t2.max_cap == t.max_cap


class TestState:
    def test_state_copy_deep(self):
        truck = make_truck()
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0))
        state = make_state(truck, [a])
        c = state.copy()
        c.package_by_id("a").position = (9, 9, 9)
        c.placements["a"] = (9, 9, 9)
        assert state.package_by_id("a").position == (0, 0, 0)

    def test_state_to_dict_from_dict_roundtrip(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0), is_fragile=True)
        b = make_package("b", w=1, l=1, h=1, position=None)
        state = make_state(truck, [a, b])
        d = state.to_dict()
        s2 = State.from_dict(d)
        assert s2.placements == state.placements
        assert s2.total_value() == state.total_value()
        assert s2.total_weight() == state.total_weight()
        assert s2.package_by_id("a").is_fragile is True
        assert s2.package_by_id("b").position is None
        assert s2.truck.dim == truck.dim

    def test_state_from_dict_mempertahankan_paket_terotasi(self):
        truck = make_truck(w=10, l=10, h=10)
        a = make_package("a", w=4, l=2, h=3, position=(0, 0, 0))
        a.rotate("z")
        state = make_state(truck, [a])
        s2 = State.from_dict(state.to_dict())
        assert s2.package_by_id("a").cur_dim == a.cur_dim
        assert s2.package_by_id("a").orient == a.orient

    def test_set_position_invalid_id(self):
        truck = make_truck()
        state = make_state(truck, [])
        with pytest.raises(KeyError):
            state.set_position("tidak_ada", (0, 0, 0))

    def test_state_summary(self):
        truck = make_truck()
        a = make_package("a", w=2, l=2, h=2, position=(0, 0, 0))
        state = make_state(truck, [a])
        assert "State" in state.summary()