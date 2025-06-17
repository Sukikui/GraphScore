from typing import Any

import networkx as nx

from metrics import find_root


def compute_mastora(
    graph: nx.DiGraph, 
    use_percentage: bool = False, 
    mode: str = "mls", 
    obstruction_attr: str = "max_transversal_obstruction"
) -> float:
    """Compute the Mastora score for a directed graph.

    Args:
        graph (nx.DiGraph): Directed graph representing the arterial tree.
        use_percentage (bool, optional): If set, treat degrees as obstruction percentages (0 to 1).
            Otherwise, use degrees (0 to 5).
        mode (str, optional): Artery levels to include: 'm' (mediastinal), 'l' (lobar), 's' (segmental).
            Any combination (e.g., 'mls').
        obstruction_attr (str, optional): The name of the edge attribute to use for obstruction values.
            Defaults to "max_transversal_obstruction".

    Returns:
        float: The Mastora score, a float between 0 and 1.
    """
    level_map = {
        "m": [1, 2],  # mediastinal
        "l": [3],  # lobar
        "s": [4],  # segmental
    }
    levels = [lvl for key in mode for lvl in level_map.get(key, [])]

    def _dfs(node: Any) -> list:
        degs = []
        for succ in graph.successors(node):
            attrs = graph.edges[node, succ]
            if attrs.get("level", 0) in levels:
                degs.append(attrs.get(obstruction_attr, 0.0))
            degs.extend(_dfs(succ))
        return degs

    root = find_root(graph)
    degrees = _dfs(root)
    return compute_mastora_score(degrees, use_percentage) if degrees else 0.0


def compute_mastora_score(degrees: list[float], use_percentage: bool = False) -> float:
    """Compute the Mastora score for a list of degrees.

    Args:
        degrees (list[float]): Degrees of the mediastinal, lobar and segmental arteries.
            Converted to integer between 0 and 5 if `use_obstruction_percentage` is False, otherwise float between
            0 and 1.
        use_percentage (bool, optional): If set, treat degrees as obstruction percentages (0 to 1).
            Otherwise, use degrees (0 to 5).

    Returns:
        float: The Mastora score, a float between 0 and 1.
    """
    if not use_percentage:
        degrees = [int(float(degree) / 0.25) + 1 for degree in degrees]
    sum_degrees = sum(degrees)
    n = len(degrees)
    return sum_degrees / n if use_percentage else sum_degrees / (n * 5)
