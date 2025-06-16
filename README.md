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

| Command | Description | Input | Options | Example Usage |
|---------|-------------|-------|---------|---------------|
| `visualize` | Create interactive HTML visualization of cumulative obstruction | JSON graph file or patient ID | `-o, --output`: Output HTML path | `visualize 0055`<br>`visualize 0055 -o viz.html` |
| `mastora` | Calculate Mastora pulmonary embolism score | JSON graph file or patient ID | None | `mastora 0055`<br>`mastora data/graphs/0055_graph_ep_transversal_obstruction.json` |
| `qanadli` | Calculate Qanadli pulmonary embolism score | JSON graph file or patient ID | None | `qanadli 0055`<br>`qanadli data/graphs/0055_graph_ep_transversal_obstruction.json` |

**Input Format**: Use either a patient ID (e.g., `0055`) or full file path. Patient IDs are auto-padded to 4 digits and resolved to `data/graphs/{id}_graph_ep_transversal_obstruction.json`.

&#160;

## NetworkX Documentation

| Function             | Underlying acyclicity | Underlying connectivity | In-degree ≤ 1 | Type       | Morgane's graphs compatibility |
| -------------------- | --------------------- | ----------------------- | ------------- | ---------- | ------------------------------ |
| `is_forest(G)`       | Yes                   | Not required            | No            | Undirected | Yes                            |
| `is_tree(G)`         | Yes                   | Yes                     | No            | Undirected | Yes                            |
| `is_branching(G)`    | Yes                   | Not required            | Yes           | Directed   | Yes                            |
| `is_arborescence(G)` | Yes                   | Yes                     | Yes           | Directed   | Yes                            |
