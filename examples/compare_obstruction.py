from pathlib import Path

from metrics import compute_cumulative_obstruction, visualize_cumulative_obstruction_pyvis
from tree import json_to_directed_graph


def compare_obstruction() -> None:
    """Compare cumulative obstruction with original obstruction."""
    graph = json_to_directed_graph(Path("../data/graphs/0055_graph_ep_transversal_obstruction.json"))
    new_graph = compute_cumulative_obstruction(graph)
    visualize_cumulative_obstruction_pyvis(new_graph, output_file="../data/graph_obstruction.html")


if __name__ == "__main__":
    compare_obstruction()
