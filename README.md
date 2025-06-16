<div align="center">

# GraphScore

Compute Scores for Pulmonary Embolism Risk

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

## CLI Commands

### `visualize`
| | |
|--|--|
| **Description** | Create interactive HTML visualization of cumulative obstruction |
| **Usage** | `visualize INPUT_FILE [OPTIONS]` |
| **Input** | JSON graph file or patient ID (e.g., `0055`) |
| **Options** | `-o, --output PATH`: Output HTML file path |
| **Examples** | `visualize 0055`<br>`visualize 0055 -o my_viz.html` |

### `mastora`
| | |
|--|--|
| **Description** | Calculate Mastora pulmonary embolism score |
| **Usage** | `mastora INPUT_FILE` |
| **Input** | JSON graph file or patient ID (e.g., `0055`) |
| **Options** | None |
| **Examples** | `mastora 0055`<br>`mastora data/graphs/0055_graph_ep_transversal_obstruction.json` |

### `qanadli`
| | |
|--|--|
| **Description** | Calculate Qanadli pulmonary embolism score |
| **Usage** | `qanadli INPUT_FILE` |
| **Input** | JSON graph file or patient ID (e.g., `0055`) |
| **Options** | None |
| **Examples** | `qanadli 0055`<br>`qanadli data/graphs/0055_graph_ep_transversal_obstruction.json` |

**Input Format**: Patient IDs are auto-padded to 4 digits and resolved to `data/graphs/{id}_graph_ep_transversal_obstruction.json`.

&#160;

## NetworkX Documentation

| Function             | Underlying acyclicity | Underlying connectivity | In-degree ≤ 1 | Type       | Morgane's graphs compatibility |
| -------------------- | --------------------- | ----------------------- | ------------- | ---------- | ------------------------------ |
| `is_forest(G)`       | Yes                   | Not required            | No            | Undirected | Yes                            |
| `is_tree(G)`         | Yes                   | Yes                     | No            | Undirected | Yes                            |
| `is_branching(G)`    | Yes                   | Not required            | Yes           | Directed   | Yes                            |
| `is_arborescence(G)` | Yes                   | Yes                     | Yes           | Directed   | Yes                            |
