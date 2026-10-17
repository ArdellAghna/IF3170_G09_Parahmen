from __future__ import annotations

from src.main import generate_test_case


class TestGenerateTestCase:
    def test_instance_reproducible(self):
        truck_a, packages_a = generate_test_case()
        truck_b, packages_b = generate_test_case()

        assert truck_a.dim == truck_b.dim
        assert truck_a.max_cap == truck_b.max_cap
        assert [p.id for p in packages_a] == [p.id for p in packages_b]
        assert [p.og_dim for p in packages_a] == [p.og_dim for p in packages_b]
        assert [p.val for p in packages_a] == [p.val for p in packages_b]
        assert [p.w for p in packages_a] == [p.w for p in packages_b]
        assert [p.is_fragile for p in packages_a] == [p.is_fragile for p in packages_b]

    def test_jumlah_paket_dan_truk(self):
        truck, packages = generate_test_case()
        assert truck.dim == {"w": 20, "l": 40, "h": 20}
        assert truck.max_cap == 2000
        assert len(packages) == 25
        assert len({p.id for p in packages}) == 25
