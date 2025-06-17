from typing import Any

import networkx as nx

from metrics import find_root


def compute_qanadli(
    graph: nx.DiGraph, min_obstruction_thresh: float = 0.25, max_obstruction_thresh: float = 0.75
) -> float:
    """Compute the Qanadli score for a directed graph.

    Args:
        graph (nx.DiGraph): Directed graph representing the arterial tree.
        min_obstruction_thresh (float, optional): Minimum obstruction threshold for considering a segment.
            Defaults to 0.25.
        max_obstruction_thresh (float, optional): Maximum obstruction threshold for considering a segment.
            Defaults to 0.75.

    Returns:
        float: The Qanadli score, a float between 0 and 1.
    """
    root = find_root(graph)
    weights: list[int] = []
    degrees: list[float] = []

    def _dfs(node: Any) -> None:
        for child in graph.successors(node):
            attrs = graph.edges[node, child]
            mto = attrs.get("max_transversal_obstruction", 0.0)
            arterie_type = get_arterie_type(attrs)
            # click.echo(f"Processing node {node} -> {child}, arterie_type: {arterie_type}, mto: {mto}")

            if arterie_type == "mediastinal" or arterie_type == "lobar":
                if mto > min_obstruction_thresh:
                    weights.append(attrs.get("segments_below", 0))
                    degrees.append(mto)
                else:
                    _dfs(child)
            elif arterie_type == "segmental":
                weights.append(1)
                degrees.append(mto)
            elif arterie_type == "root":
                _dfs(child)

    _dfs(root)
    # click.echo(weights)
    # click.echo(degrees)
    return compute_qanadli_score(weights, degrees, min_obstruction_thresh, max_obstruction_thresh) if degrees else 0.0


def get_arterie_type(edge: dict[str, Any]) -> str:
    """Get the type of artery based on the edge attributes.

    Args:
        edge (dict[str, Any]): Edge attributes containing 'level'.

    Returns:
        str: Type of artery ('root', 'mediastinal', 'lobar' or 'segmental').
    """
    level = edge.get("level", 0)
    if level == 1:
        return "root"
    if level == 2:
        return "mediastinal"
    if level == 4:
        return "segmental"
    if level == 3:
        if all(succ.get("level", 0) == 4 for succ in edge.get("successors", [])):
            return "lobar"  # return "segmental" in normal cases
        return "lobar"
    return ""


def compute_qanadli_score(
    weights: list[int], degrees: list[float], min_obstruction_thresh: float, max_obstruction_thresh: float
) -> float:
    """Compute the Qanadli score for a list of degrees.

    Args:
        weights (list[int]): Weights of the segments, representing the number of segments below each artery.
        degrees (list[float]): Degrees of obstruction for each segment.
        min_obstruction_thresh (float): Minimum obstruction threshold for considering a segment.
        max_obstruction_thresh (float): Maximum obstruction threshold for considering a segment.

    Returns:
        float: The Qanadli score, a float between 0 and 1.
    """
    degrees = [
        0 if degree < min_obstruction_thresh else 1 if degree < max_obstruction_thresh else 2 for degree in degrees
    ]
    weighted_degrees = [weight * degree for weight, degree in zip(weights, degrees, strict=False)]
    return sum(weighted_degrees) / (2 * sum(weights))
