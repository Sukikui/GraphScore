from pathlib import Path

from metrics.custom import compute_cumulative_obstruction, visualize_cumulative_obstruction_pyvis
from tree.io import json_to_directed_graph


def compare_obstruction() -> None:
    """Compare cumulative obstruction with original obstruction."""
    graph = json_to_directed_graph(Path("../data/graphs/0222_graph_ep.json"))
    new_graph = compute_cumulative_obstruction(graph)
    # Cumulative
    visualize_cumulative_obstruction_pyvis(new_graph, output_file="../data/graph_obstruction.html")
    # Original
    visualize_cumulative_obstruction_pyvis(
        graph, obstruction_attr="ep_vessels_occupancy", output_file="../data/graph_obstruction2.html"
    )


if __name__ == "__main__":
    compare_obstruction()
