<div align="center">

# GraphScore

Compute Scores for Pulmonary Embolism Risk Assessment from Arterial Tree Graphs

</div>

&#160;

## Installation

Install [uv](https://docs.astral.sh/uv/) if you don't have it already.

```bash
pip install uv
```

Create a virtual environment using uv and sync the dependencies.

```bash
uv venv
source .venv/bin/activate
uv sync
```

&#160;

## Project Structure

- `graphscore/`: Core CLI implementation
- `tree/`: Graph modeling, processing, and I/O utilities
- `metrics/`: Implementation of scoring algorithms (Mastora, Qanadli) and visualization
- `data/graphs/`: Storage location for patient graph data files

&#160;

## CLI Commands

### `mastora`

| **Description** | Compute Mastora score for pulmonary embolism risk assessment                                                                                                                                                                                                                                         |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usage**       | `mastora INPUT_FILE [OPTIONS]`                                                                                                                                                                                                                                                                       |
| **Input**       | JSON graph file or patient ID (e.g., `0055`)                                                                                                                                                                                                                                                         |
| **Options**     | `--use-percentage`: Treat degrees as obstruction percentages (0 to 1)<br>`--mode TEXT`: Artery levels to include: 'm' (mediastinal), 'l' (lobar), 's' (segmental). Default: 'mls'<br>`--obstruction-attr TEXT`: Edge attribute to use for obstruction values. Default: 'max_transversal_obstruction' |
| **Examples**    | `mastora 55`<br>`mastora 0055 --use-percentage --mode mls`                                                                                                                                                                                                                                           |

### `qanadli`

| **Description** | Compute Qanadli score for pulmonary embolism risk assessment                                                                                                                                                                                                                                                                            |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usage**       | `qanadli INPUT_FILE [OPTIONS]`                                                                                                                                                                                                                                                                                                          |
| **Input**       | JSON graph file or patient ID (e.g., `0055`)                                                                                                                                                                                                                                                                                            |
| **Options**     | `--min-obstruction-thresh FLOAT`: Minimum obstruction threshold for considering a segment. Default: 0.25<br>`--max-obstruction-thresh FLOAT`: Maximum obstruction threshold for considering a segment. Default: 0.75<br>`--obstruction-attr TEXT`: Edge attribute to use for obstruction values. Default: 'max_transversal_obstruction' |
| **Examples**    | `qanadli 55`<br>`qanadli 0055 --min-obstruction-thresh 0.3 --max-obstruction-thresh 0.8`                                                                                                                                                                                                                                                |

### `visualize`

| **Description** | Visualize cumulative obstruction using PyVis interactive network                                                |
| --------------- | --------------------------------------------------------------------------------------------------------------- |
| **Usage**       | `visualize INPUT_FILE [OPTIONS]`                                                                                |
| **Input**       | JSON graph file or patient ID (e.g., `0055`)                                                                    |
| **Options**     | `--obstruction-attr TEXT`: Edge attribute to use for obstruction values. Default: 'max_transversal_obstruction' |
| **Examples**    | `visualize 0055`<br>`visualize 55 --obstruction-attr max_transversal_obstruction`                               |

**Input Format**: Patient IDs are auto-padded to 4 digits and resolved to `data/graphs/{id}_graph_ep_transversal_obstruction.json`.

&#160;

## NetworkX Documentation

| Function             | Underlying acyclicity | Underlying connectivity | In-degree ≤ 1 | Type       | Morgane's graphs compatibility |
| -------------------- | --------------------- | ----------------------- | ------------- | ---------- | ------------------------------ |
| `is_forest(G)`       | Yes                   | Not required            | No            | Undirected | Yes                            |
| `is_tree(G)`         | Yes                   | Yes                     | No            | Undirected | Yes                            |
| `is_branching(G)`    | Yes                   | Not required            | Yes           | Directed   | Yes                            |
| `is_arborescence(G)` | Yes                   | Yes                     | Yes           | Directed   | Yes                            |
