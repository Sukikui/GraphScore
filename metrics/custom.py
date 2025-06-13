from typing import Any, Callable, Dict, Tuple
import networkx as nx


def compute_cumulative_obstruction(
    graph: nx.DiGraph,
    root: Any = None,
    root_obstruction: float = 0.0,
    edge_attr: str = "ep_vessels_occupancy",
    combine_fn: Callable[[float, float], float] | None = None,
) -> Dict[Tuple[Any, Any], float]:
    """
    Traverse the directed tree graph starting from the specified root node,
    and compute a cumulative obstruction value for each edge (u, v).

    Args:
        graph (nx.DiGraph): A valid directed acyclic graph representing an arborescence.
        root (Any): The root node of the tree (node with in-degree == 0).
        root_obstruction (float): The initial obstruction value for the root node.
            Defaults to 0.0.
        edge_attr (str): The name of the edge attribute containing the raw obstruction degree.
            Defaults to "ep_vessels_occupancy".
        combine_fn (Callable[[float, float], float] | None): A function that takes the parent's
            cumulative obstruction and the edge's own obstruction degree, and returns the new
            cumulative value. Defaults to max(parent_deg, own_deg) if None.

    Returns:
        Dict[Tuple[Any, Any], float]: A mapping from each edge (u, v) to its computed
            cumulative obstruction value.
    """
    if root is None:
        root = find_root(graph)

    if combine_fn is None:
        def combine_fn(parent_deg: float, own_deg: float) -> float:
            return max(parent_deg, own_deg)

    cum_obstruction: Dict[Tuple[Any, Any], float] = {}

    def dfs(node: Any, parent_cum_deg: float) -> None:
        for child in graph.successors(node):
            own_deg = graph.edges[node, child].get(edge_attr, 0.0)
            cum_deg = combine_fn(parent_cum_deg, own_deg)
            cum_obstruction[(node, child)] = cum_deg
            dfs(child, cum_deg)

    dfs(root, root_obstruction)
    return cum_obstruction


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

