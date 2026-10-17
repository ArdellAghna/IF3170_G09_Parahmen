#python scripts/make_plots.py output/ output/plots/

from __future__ import annotations

import glob
import json
import os
import sys
from collections import defaultdict
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def load(output_dir: str) -> List[Dict]:
    data = []
    for path in sorted(glob.glob(os.path.join(output_dir, "*.json"))):
        with open(path, encoding="utf-8") as f:
            item = json.load(f)
        item["_file"] = os.path.basename(path)
        data.append(item)
    return data


def plot_hc(runs: List[Dict], out_dir: str) -> None:
    variants = sorted({r["variant"] for r in runs})
    for variant in variants:
        subset = [r for r in runs if r["variant"] == variant]
        plt.figure(figsize=(9, 4.5))
        for r in subset:
            plt.plot(r["history"], label=r["_file"], linewidth=1.2)
        plt.title(f"Hill Climbing ({variant}) - Objective vs Iterasi")
        plt.xlabel("Iterasi")
        plt.ylabel("Objective (best)")
        plt.legend(fontsize=7)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"hc_{variant}_objective.png"), dpi=130)
        plt.close()


def plot_sa(runs: List[Dict], out_dir: str) -> None:
    plt.figure(figsize=(9, 4.5))
    for r in runs:
        plt.plot(r["history"], label=r["_file"], linewidth=1.2)
    plt.title("Simulated Annealing - Objective vs Iterasi")
    plt.xlabel("Iterasi")
    plt.ylabel("Objective (best)")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "sa_objective.png"), dpi=130)
    plt.close()

    plt.figure(figsize=(9, 4.5))
    for r in runs:
        probs = r.get("metrics", {}).get("prob_history", [])
        plt.plot(probs, label=r["_file"], linewidth=1.0)
    plt.title("Simulated Annealing - e^(dE/T) vs Iterasi")
    plt.xlabel("Iterasi")
    plt.ylabel("e^(dE/T)")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "sa_probability.png"), dpi=130)
    plt.close()

    labels = [r["_file"] for r in runs]
    stuck = [r.get("metrics", {}).get("stuck_count", 0) for r in runs]
    plt.figure(figsize=(7, 4))
    plt.bar(labels, stuck, color="#f59e0b")
    plt.title("Simulated Annealing - Frekuensi Stuck")
    plt.ylabel("stuck_count")
    plt.xticks(rotation=15, fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "sa_stuck.png"), dpi=130)
    plt.close()


def _config_key(r: Dict) -> str:
    params = r["params"]
    scenario = "A" if r["_file"].startswith("ga_A") else "B"
    return f"{scenario}: pop={params.get('pop_size')}, gen={params.get('max_generations')}"


def plot_ga(runs: List[Dict], out_dir: str) -> None:
    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for r in runs:
        grouped[_config_key(r)].append(r)

    for config, subset in sorted(grouped.items()):
        plt.figure(figsize=(9, 4.5))
        for r in subset:
            label = r["_file"].replace("ga_", "").replace(".json", "")
            plt.plot(r["history"], label=f"{label} (max)", linewidth=1.2)
            avg = r.get("metrics", {}).get("avg_history", [])
            plt.plot(avg, linestyle="--", linewidth=1.0, label=f"{label} (avg)")
        plt.title(f"Genetic Algorithm {config} - Objective Max & Avg")
        plt.xlabel("Generasi")
        plt.ylabel("Objective")
        plt.legend(fontsize=6)
        plt.tight_layout()
        safe = config.replace(":", "").replace(" ", "").replace(",", "_").replace("=", "")
        plt.savefig(os.path.join(out_dir, f"ga_{safe}.png"), dpi=130)
        plt.close()


def plot_durations(data: List[Dict], out_dir: str) -> None:
    buckets: Dict[str, List[float]] = defaultdict(list)
    for r in data:
        key = r["algorithm"] + (f" ({r['variant']})" if r.get("variant") else "")
        buckets[key].append(r["duration"])

    labels = sorted(buckets)
    means = [sum(buckets[k]) / len(buckets[k]) for k in labels]

    plt.figure(figsize=(10, 4.5))
    plt.bar(labels, means, color="#3b82f6")
    plt.title("Perbandingan Rata-rata Durasi Pencarian")
    plt.ylabel("detik")
    plt.xticks(rotation=30, ha="right", fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "durasi_rata_rata.png"), dpi=130)
    plt.close()


def main() -> int:
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(output_dir, "plots")
    os.makedirs(out_dir, exist_ok=True)

    data = load(output_dir)
    if not data:
        print(f"Tidak ada berkas JSON di {output_dir}")
        return 1

    plot_hc([r for r in data if r["algorithm"] == "hill_climbing"], out_dir)
    plot_sa([r for r in data if r["algorithm"] == "simulated_annealing"], out_dir)
    plot_ga([r for r in data if r["algorithm"] == "genetic_algorithm"], out_dir)
    plot_durations(data, out_dir)

    print(f"Plot tersimpan di {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
