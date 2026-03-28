# Genetic Algorithm for the Traveling Salesman Problem (TSP)

A Python coursework project that solves **TSP instances** with a **genetic algorithm**, using a remote API to fetch city data and submit tours for server-side validation and ranking.

## What it does

The **Traveling Salesman Problem** asks for the shortest round trip that visits every city exactly once and returns to the start. This repository implements a classic evolutionary loop:

1. **Initialize** a population of candidate tours  
2. **Evaluate** each tour with a **fitness** function (total Euclidean length of the closed route)  
3. **Select** parents (roulette or elitism)  
4. **Vary** the population (permutation-based mutation; optional one-point crossover)  
5. Repeat for a fixed number of **generations**, then return the best tour  

The best tour is converted to a list of **city indices** (relative to the original instance) and sent to the API as required by the assignment server.

## Highlights

- **REST integration** with [`requests`](https://requests.readthedocs.io/): `GET` instances, `POST` solutions  
- **Smarter initialization**: nearest-neighbor–style construction with randomness among the *k* closest unvisited cities, instead of purely random permutations  
- **Two selection schemes**: weighted roulette (favor shorter tours) and **elitism** (keep the top *n* individuals)  
- **Controlled mutation**: swap a small number of positions per offspring (`n_perm`); empirically, low values (e.g. `2`) work better with elitism  
- **Optional crossover** (`crossover_method="simple"`): implemented but disabled in our main experiments when it did not improve quality  

## Repository layout

| File | Role |
|------|------|
| `Config.py` | Core GA: `init`, `evaluation`, `fitness`, `selection`, `mutation`, `crossover`, `main`, plus `fetch_data` / `upload_result` |
| `tp6_tiny.py` | Example script: fetch instance → run GA → submit result |
| `tp6_small.py` | Alternate experiment (different instance / parameters) |
| `compte_rendu.md` | Detailed report (French) |

## Requirements

- Python 3.x  
- `numpy`  
- `requests`  

Install dependencies (example):

```bash
pip install numpy requests
```

## Quick start

From the project root:

```bash
python tp6_tiny.py
```

Edit `tp6_tiny.py` to set:

- `instance_id` — server instance name (e.g. `hard_hierarchical`, `regions`, …)  
- `student_id` — your identifier for submission  
- GA parameters passed to `Config.main(...)`: population size, generations, selection method, `n_perm`, `n_elitism`, etc.  

Example call shape:

```python
result = Config.main(
    instances=data["cities"],
    selection_method="elitisme",
    mutation_method="permutation",
    n_loop=1000,
    n_individus=300,
    n_perm=2,
    n_elitism=30,
)
response = Config.upload_result(
    student_id=student_id,
    instance_id=instance_id,
    initial_instances=data["cities"],
    result=result,
)
```

## API (assignment server)

- **Instances**: `GET https://tsp-sra0.onrender.com/instances/{instance_id}`  
- **Submit**: `POST https://tsp-sra0.onrender.com/submit` with JSON  
  `{ "student_id", "instance_id", "tour": [ ... indices ... ] }`  

The `upload_result` helper builds `tour` from the ordered list of coordinates, including correct handling when duplicate coordinates appear in the instance.

## Parameters (practical notes)

- **`n_perm`**: small values keep mutations local; large values tend to destroy good elite tours.  
- **`n_elitism`**: often set to ~10% of `n_individus` (e.g. 30 / 300).  
- **`n_loop` / `n_individus`**: trade-off between solution quality and runtime on your machine.
- **`n_crossover`**: often set to 50% of the number of "cities".

## Authors & context

University lab project (genetic algorithms / combinatorial optimization).  
Code comments and the written report `compte_rendu.md` are in **French**; this README is in **English** for portfolio visibility.

## License

This repository is provided for educational and portfolio purposes. Add a license file if you need explicit terms for reuse.
