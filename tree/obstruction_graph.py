from collections.abc import Callable
from typing import Any

import networkx as nx


def add_max_cumulative_obstruction(
    graph: nx.DiGraph,
    root: Any = None,
    root_obstruction: float = 0.0,
    input_attr: str = "transversal_obstruction",
    max_attr: str = "max_transversal_obstruction",
    cumulative_attr: str = "cumulative_max_transversal_obstruction",
    combine_fn: Callable[[float, float], float] | None = None,
) -> nx.DiGraph:
    """Traverse the directed tree and return a copy with propagated obstruction on each edge.

    Traverses the arborescence `graph` from `root`, computes a cumulative obstruction value
    for each edge by combining the parent's propagated obstruction with the edge's own raw
    obstruction attribute, and stores the result in a new edge attribute.

    Args:
        graph (nx.DiGraph): Directed acyclic graph representing an arborescence.
        root (Any, optional): The root node (in-degree == 0). If None, it is auto-detected.
            Defaults to None.
        root_obstruction (float, optional): Initial obstruction value at the root. Default to 0.0.
        input_attr (str, optional): Name of the edge attribute with the raw obstruction degree.
            Defaults to "ep_vessels_occupancy".
        max_attr (str, optional): Name of the edge attribute with the maximum obstruction degree.
            Defaults to "max_transversal_obstruction".
        cumulative_attr (str, optional): Name for the new edge attribute to store propagated
            obstruction. Defaults to "cumulative_obstruction".
        combine_fn (Callable[[float, float], float], optional): Function taking
            (parent_cum_deg, own_deg) → new cumulative degree. Defaults to max(parent, own).

    Returns:
        nx.DiGraph: A shallow copy of `graph` where each edge has `output_attr` set to its
        computed cumulative obstruction.

    Raises:
        ValueError: If `graph` is not a valid arborescence.
    """
    if root is None:
        root = find_root(graph)

    if combine_fn is None:

        def combine_fn(parent_deg: float, own_deg: float) -> float:
            return max(parent_deg, own_deg)

    new_graph = graph.copy()

    def _dfs(node: Any, parent_cum: float) -> None:
        for child in new_graph.successors(node):
            own = new_graph.edges[node, child].get(input_attr, [0.0])
            own = max(own)
            cum = combine_fn(parent_cum, own)
            new_graph.edges[node, child][max_attr] = own
            new_graph.edges[node, child][cumulative_attr] = cum
            _dfs(child, cum)

    _dfs(root, root_obstruction)
    return new_graph


def find_root(graph: nx.DiGraph) -> Any:
    """Find the unique root node (in-degree == 0) in a directed tree.

    Args:
        graph (nx.DiGraph): A directed acyclic graph representing an arborescence where each node
            has in-degree ≤ 1 and the underlying undirected graph is connected.

    Returns:
        Any: The root node of the tree (the only node with in-degree 0).

    Raises:
        ValueError: If no node with in-degree 0 is found.
        ValueError: If more than one node with in-degree 0 is found.
    """
    roots = [node for node, deg in graph.in_degree() if deg == 0]
    if not roots:
        raise ValueError("No root found: graph has no node with in-degree 0.")
    if len(roots) > 1:
        raise ValueError(f"Multiple roots found: {roots}")
    return roots[0]
