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
        assert truck.dim == {"w": 14, "l": 24, "h": 12}
        assert truck.max_cap == 450
        assert len(packages) == 40
        assert len({p.id for p in packages}) == 40

    def test_kendala_mengikat(self):
        truck, packages = generate_test_case()
        total_weight = sum(p.w for p in packages)
        total_volume = sum(p.og_dim["w"] * p.og_dim["l"] * p.og_dim["h"] for p in packages)
        truck_volume = truck.dim["w"] * truck.dim["l"] * truck.dim["h"]
        assert total_weight > truck.max_cap
        assert total_volume > 0.5 * truck_volume
