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

## CLI Usage

GraphScore provides three command-line tools for computing pulmonary embolism risk scores:

### Commands

#### `visualize`
Visualize cumulative obstruction from a graph JSON file.

```bash
visualize INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Input JSON graph file. You can provide either:
  - Full file path to a JSON graph file
  - Patient ID only (e.g., `0055`) - will automatically locate the corresponding graph file

**Options:**
- `-o, --output PATH`: Output HTML file path (default: `graph_obstruction.html`)

**Examples:**
```bash
# Using patient ID
visualize 0055

# Using full file path
visualize data/graphs/0055_graph_ep_transversal_obstruction.json

# Specify custom output file
visualize 0055 -o my_visualization.html
```

#### `mastora`
Compute Mastora score from a graph JSON file.

```bash
mastora INPUT_FILE
```

**Arguments:**
- `INPUT_FILE`: Input JSON graph file (same format as visualize command)

**Examples:**
```bash
mastora 0055
mastora data/graphs/0055_graph_ep_transversal_obstruction.json
```

#### `qanadli`
Compute Qanadli score from a graph JSON file.

```bash
qanadli INPUT_FILE
```

**Arguments:**
- `INPUT_FILE`: Input JSON graph file (same format as visualize command)

**Examples:**
```bash
qanadli 0055
qanadli data/graphs/0055_graph_ep_transversal_obstruction.json
```

### File Path Resolution

For convenience, you can use just the patient ID (e.g., `0055`) instead of the full file path. The CLI will automatically search for files in:
1. `../data/graphs/{patient_id}_graph_ep_transversal_obstruction.json`
2. `data/graphs/{patient_id}_graph_ep_transversal_obstruction.json`

Patient IDs are automatically zero-padded to 4 digits (e.g., `55` becomes `0055`).

&#160;

## NetworkX Documentation

| Function             | Underlying acyclicity | Underlying connectivity | In-degree ≤ 1 | Type       | Morgane's graphs compatibility |
| -------------------- | --------------------- | ----------------------- | ------------- | ---------- | ------------------------------ |
| `is_forest(G)`       | Yes                   | Not required            | No            | Undirected | Yes                            |
| `is_tree(G)`         | Yes                   | Yes                     | No            | Undirected | Yes                            |
| `is_branching(G)`    | Yes                   | Not required            | Yes           | Directed   | Yes                            |
| `is_arborescence(G)` | Yes                   | Yes                     | Yes           | Directed   | Yes                            |
