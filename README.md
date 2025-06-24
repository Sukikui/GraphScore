<div align="center">

# GraphScore

Compute Scores for Pulmonary Embolism Risk from Arterial Tree Graphs

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
- `data/cumulative_graphs/`: Default storage for cumulative obstruction generated graphs

&#160;

## CLI Commands

**Input Format**: Patient IDs are auto-padded to 4 digits and resolved to `data/graphs/{id}_graph_ep_transversal_obstruction.json`.

### ▶️ `mastora`

| **Description** | Compute Mastora score for pulmonary embolism risk                                                                                                                                                                                                                                                                                                                                        |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usage**       | `mastora INPUT_FILE [OPTIONS]`                                                                                                                                                                                                                                                                                                                                                           |
| **Input**       | JSON graph file or patient ID (e.g., `0055`)                                                                                                                                                                                                                                                                                                                                             |
| **Options**     | `--use-percentage, -p`: Treat degrees as obstruction percentages (0 to 1)<br>`--mode, -m TEXT`: Artery levels to include: 'm' (mediastinal), 'l' (lobar), 's' (segmental). Default: 'mls'<br>`--obstruction-attr, -o TEXT`: Edge attribute to use for obstruction values. Default: 'max_transversal_obstruction'<br>`--debug, -d`: Show a debug visualization of the Mastora calculation |
| **Examples**    | `mastora 55`<br>`mastora 0055 -p -m mls`<br>`mastora 0055 -d`                                                                                                                                                                                                                                                                                                                            |

### ▶️ `qanadli`

| **Description** | Compute Qanadli score for pulmonary embolism risk                                                                                                                                                                                                                                                                                                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usage**       | `qanadli INPUT_FILE [OPTIONS]`                                                                                                                                                                                                                                                                                                                                                                                              |
| **Input**       | JSON graph file or patient ID (e.g., `0055`)                                                                                                                                                                                                                                                                                                                                                                                |
| **Options**     | `--min-obstruction-thresh, -n FLOAT`: Minimum obstruction threshold for considering a segment. Default: 0.25<br>`--max-obstruction-thresh, -x FLOAT`: Maximum obstruction threshold for considering a segment. Default: 0.75<br>`--obstruction-attr, -o TEXT`: Edge attribute to use for obstruction values. Default: 'max_transversal_obstruction'<br>`--debug, -d`: Show a debug visualization of the Qanadli calculation |
| **Examples**    | `qanadli 55`<br>`qanadli 0055 -n 0.3 -x 0.8`<br>`qanadli 0055 -d`                                                                                                                                                                                                                                                                                                                                                           |

### ▶️ `generate-cumulative`

| **Description** | Generate cumulative obstruction graph and save it to NetworkX JSON file                                         |
| --------------- | --------------------------------------------------------------------------------------------------------------- |
| **Usage**       | `generate-cumulative [INPUT_FILE] [OPTIONS]`                                                                    |
| **Input**       | JSON graph file or patient ID (e.g., `0055`). If omitted, processes all graphs in the data/graphs directory     |
| **Options**     | `--output-dir, -d TEXT`: Directory where to save the cumulative graph files. Default: 'data/cumulative_graphs/' |
| **Examples**    | `generate-cumulative 0055`<br>`generate-cumulative 55 -d custom/output/dir/`<br>`generate-cumulative`           |

### ▶️ `visualize`

| **Description** | Visualize cumulative obstruction using PyVis interactive network                                                    |
| --------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Usage**       | `visualize INPUT_FILE [OPTIONS]`                                                                                    |
| **Input**       | JSON graph file or patient ID (e.g., `0055`)                                                                        |
| **Options**     | `--obstruction-attr, -o TEXT`: Edge attribute to use for obstruction values. Default: 'max_transversal_obstruction' |
| **Examples**    | `visualize 0055`<br>`visualize 55 -o max_transversal_obstruction`                                                   |

### List of `--obstruction-attr`

| **Attribute**                            | **Description**                                                       |
| ---------------------------------------- | --------------------------------------------------------------------- |
| `max_transversal_obstruction`            | Maximum transversal obstruction value across one segment of the graph |
| `max_transversal_obstruction_propagated` | `own_mto = max(parent_mto, own_mto)`                                  |
| `max_transversal_obstruction_cumulated`  | `own_mto = 1 - (1 - parent_mto) * (1 - own_mto)`                      |

#### Visualization Examples

<div align="center">
  <table width="100%">²
    <tr>
      <td width="50%" align="center"><b><code>visualize 55 -o max_transversal_obstruction</code></b></td>
      <td width="50%" align="center"><b><code>visualize 55 -o max_transversal_obstruction_cumulated</code></b></td>
    </tr>
    <tr>
      <td width="50%" align="center"><img src="assets/original_graph.png" width="450"></td>
      <td width="50%" align="center"><img src="assets/cumulative_graph.png" width="450"></td>
    </tr>
  </table>
</div>

&#160;

## NetworkX Documentation

| Function             | Underlying acyclicity | Underlying connectivity | In-degree ≤ 1 | Type       | Morgane's graphs compatibility |
| -------------------- | --------------------- | ----------------------- | ------------- | ---------- | ------------------------------ |
| `is_forest(G)`       | Yes                   | Not required            | No            | Undirected | Yes                            |
| `is_tree(G)`         | Yes                   | Yes                     | No            | Undirected | Yes                            |
| `is_branching(G)`    | Yes                   | Not required            | Yes           | Directed   | Yes                            |
| `is_arborescence(G)` | Yes                   | Yes                     | Yes           | Directed   | Yes                            |
