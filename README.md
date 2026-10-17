# IF3170_G09_Parahmen - 3D Truck Loading Optimization

Tugas Besar 1 IF3170 Inteligensi Artifisial. Tugas ini menyelesaikan persoalan **3D Truck Loading Optimization** menggunakan pendekatan *local search*: memaksimalkan total value paket yang dimuat ke dalam peti kemas truk dengan tetap memenuhi seluruh kendala fisik.

## Algoritma

- **Hill Climbing** dengan empat varian: `steepest`, `sideways`, `restart`, dan `stochastic`.
- **Simulated Annealing** dengan step pendinginan secara eksponensial.
- **Genetic Algorithm** dengan roulette wheel selection, crossover satu titik, dan mutasi.

## Struktur Folder

```
src/
  algoritma/        hill_climbing.py, simulated_annealing.py, genetic_algorithm.py
  model/            package.py, truck.py, state.py, result.py
  constraints.py    aturan feasibility (bounds, overlap, support, fragile, kapasitas)
  objective.py      fungsi objektif
  moves.py          operator swap, relocate, rotate + generator tetangga
  init.py           inisialisasi random
  main.py           runner seluruh percobaan
  config.py         parameter perocbaan
tests/              unit test
output/             hasil percobaan (.json) dan plot
visualisasi/        visualisasi 3D berbasis web (Three.js + Chart.js)
scripts/            validate_outputs.py, make_plots.py
```

## Kebutuhan

- Python 3.10 atau lebih baru
- Dependensi pada `requirements.txt`: `pytest`, `numpy`, `matplotlib`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan Test

```bash
python -m pytest
```

## Menjalankan Eksperimen

```bash
python -m src.main
```

Catatan:
- Menjalankan perintah ini akan **menimpa** berkas hasil di `output/`.
- Seluruh eksperimen memakan waktu sekitar **35-40 menit**, didominasi Hill Climbing Random Restart.
- Hasil disimpan sebagai JSON, satu berkas per run`.


Membuat grafik:

```bash
python scripts/make_plots.py output/ output/plots/
```

## Visualisasi 3D

Buka `visualisasi/index.html` langsung di browser, atau lewat server lokal:

```bash
python -m http.server 8000
# buka http://localhost:8000/visualisasi/
```

Pilih salah satu berkas JSON dari `output/`.

## Catatan

- Untuk test menggunkakan seed `317009` agar hasil test dengan laporan selalu sama tidak berubah ubah dengan total nilai 1273.
- `random_initial_state` menghasilkan state awal acak dan dijamin feasible.

## Pembagian Tugas

| Nama | NIM | Pekerjaan |
|---|---|---|
| Ardell Aghna Mahendra |13523151| Silahkan isi |
| Fazri Arrashyi Putra |13524127| Inisiasi Tugas, 4 Algoritma HC, Testing & Laporan |
| Dzakwan Muhammad Khairan Putra Purnama |13524145| Silahkan isi |
