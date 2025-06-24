from typing import Any

import networkx as nx


def add_max_attribute_values(
    graph: nx.DiGraph,
    root: Any = None,
    root_obstruction: float = 0.0,
    input_attr: str = "transversal_obstruction",
    max_attr: str = "max_transversal_obstruction",
    propagated_attr: str = "max_transversal_obstruction_propagated",
    cumulated_attr: str = "max_transversal_obstruction_cumulated",
) -> nx.DiGraph:
    """Traverse the directed tree and return a copy with computed attribute values on each edge.

    Traverses the arborescence `graph` from `root`, computes derived attribute values
    for each edge by combining the parent's computed values with the edge's own raw
    attribute values, and stores the results in new edge attributes.

    Args:
        graph (nx.DiGraph): Directed acyclic graph representing an arborescence.
        root (Any, optional): The root node (in-degree == 0). If None, it is auto-detected.
            Defaults to None.
        root_obstruction (float, optional): Initial attribute value at the root. Default to 0.0.
        input_attr (str, optional): Name of the edge attribute with the raw values.
            Defaults to "transversal_obstruction".
        max_attr (str, optional): Name of the edge attribute with the maximum values.
            Defaults to "max_transversal_obstruction".
        propagated_attr (str, optional): Name for the new edge attribute to store propagated
            values. Defaults to "max_transversal_obstruction_propagated".
        cumulated_attr (str, optional): Name for the new edge attribute to store cumulated
            values. Defaults to "max_transversal_obstruction_cumulated".

    Returns:
        nx.DiGraph: A shallow copy of `graph` where each edge has computed attribute values.

    Raises:
        ValueError: If `graph` is not a valid arborescence.
    """
    new_graph = graph.copy()
    if root is None:
        root = find_root(graph)

    def propagate_fn(parent_deg: float, own_deg: float) -> float:
        """Return new propagated attribute value for the edge based on parent's and own values."""
        return max(parent_deg, own_deg)

    def cumulate_fn(parent_deg: float, own_deg: float) -> float:
        """Return new cumulated attribute value for the edge based on parent's and own values."""
        return 1 - (1 - own_deg) * (1 - parent_deg)

    def _dfs(node: Any, parent_prop: float, parent_cum: float) -> None:
        for child in new_graph.successors(node):
            own = new_graph.edges[node, child].get(input_attr, [0.0])
            own = max(own)
            prop = propagate_fn(parent_prop, own)
            cum = cumulate_fn(parent_cum, own)
            new_graph.edges[node, child][max_attr] = own
            new_graph.edges[node, child][propagated_attr] = prop
            new_graph.edges[node, child][cumulated_attr] = cum
            _dfs(child, prop, cum)

    _dfs(root, root_obstruction, root_obstruction)
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
