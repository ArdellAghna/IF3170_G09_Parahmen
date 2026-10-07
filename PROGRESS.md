# Progress bagian core + moves + hill climbing

Update terakhir: 7 Oktober 2026

Hai kak halo wan, ini catatan log nya

## Yang udah jadi

### model (`src/model/`)

- `package.py` -> `Package`. Intinya buat paket nya.
- `truck.py` -> `Truck`, Ini buat treuk.
- `state.py` -> `State`, Buat penempatan paket sekaligus state lainnya.
- `result.py` -> `Result`, ini buat result nya biar sama

### constraint (`src/constraints.py`) intinya aturan aturan misal biar paket nya ga nembus dinding, tabrakan dsb..

### objective (`src/objective.py`)

- `objective(state)` -> total value paket di dalam truk. Kalo state-nya infeasible, skornya negatif.
- `feasible_value(state)` -> Nah ini buat nanti test di laporan.

### moves (`src/moves.py`) Buat pergerakan paket

### init (`src/init.py`)

- `random_initial_state(truck, packages, rng)` -> state awal acak yang dijamin feasible.

### hill climbing (`src/algoritma/hill_climbing.py`)

- 4 varian: `steepest`, `sideways`, `restart`, `stochastic` (bonus nya udah ya)

### utilitas (`src/utilitas/helpers.py`)

### Run nya pake .venv
