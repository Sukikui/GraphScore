import json
from pathlib import Path

import networkx as nx


def json_to_directed_graph(json_path: Path, **node_link_graph_kwargs) -> nx.DiGraph:
    """Parses JSON file into a NetworkX `DiGraph`.

    Args:
        json_path: File path to read as NetworkX graph.
        **node_link_graph_kwargs: Keys for serialized attribute names to pass to `nx.node_link_graph`.

    Returns:
        NetworkX `DiGraph` loaded from the JSON file.
    """
    with open(json_path) as file:
        json_graph = json.load(file)

    graph = nx.node_link_graph(
        json_graph,
        directed=True,
        **node_link_graph_kwargs or {"edges": "links"},
    )

    if not nx.is_arborescence(graph):
        raise ValueError("The DiGraph is not an arborescence.")
    return nx.DiGraph(graph)
