import os
import webbrowser
from collections.abc import Callable
from typing import Any

import networkx as nx
from matplotlib.colors import LinearSegmentedColormap, Normalize
from pyvis.network import Network


def compute_cumulative_obstruction(
    graph: nx.DiGraph,
    root: Any = None,
    root_obstruction: float = 0.0,
    edge_attr: str = "ep_vessels_occupancy",
    combine_fn: Callable[[float, float], float] | None = None,
) -> dict[tuple[Any, Any], float]:
    """Traverse the directed tree graph starting from the specified root node.

    Compute a cumulative obstruction value for each edge (u, v).

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

    cum_obstruction: dict[tuple[Any, Any], float] = {}

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


def visualize_cumulative_obstruction_pyvis(
    graph: nx.DiGraph,
    cum_obstruction: dict[tuple[Any, Any], float],
    height: str = "1400px",
    width: str = "100%",
    bgcolor: str = "#000000",
    font_color: str = "#ffffff",
    min_edge_width: float = 1.0,
    max_edge_width: float = 5.0,
    output_file: str = "graph_obstruction.html",
) -> None:
    """Render an interactive HTML visualization of a directed tree.

    Edges are colored from yellow (low obstruction) to red (high obstruction)
    and width proportional to obstruction.

    Args:
        graph (nx.DiGraph): Directed tree structure.
        cum_obstruction (Dict[Tuple[Any, Any], float]):
            Mapping from each edge (u, v) to its cumulative obstruction value in [0,1].
        height (str): Height of the HTML canvas. Defaults to "750px".
        width (str): Width of the HTML canvas. Defaults to "100%".
        bgcolor (str): Background color. Defaults to black.
        font_color (str): Node label color. Defaults to white.
        min_edge_width (float): Width for edges with zero obstruction. Defaults to 1.0.
        max_edge_width (float): Width for edges with full obstruction. Defaults to 5.0.
        output_file (str): Path to write the HTML file. Defaults to "graph_obstruction.html".
    """
    # normalize values
    values = list(cum_obstruction.values())
    vmin, vmax = min(values, default=0.0), max(values, default=1.0)
    norm = Normalize(vmin=vmin, vmax=(vmax or 1.0))

    # yellow → red colormap
    yellow_red = LinearSegmentedColormap.from_list("yellow_red", ["#ffff00", "#ff0000"])

    # prepare PyVis
    net = Network(height=height, width=width, bgcolor=bgcolor, font_color=font_color, directed=True, notebook=False)
    net.force_atlas_2based()

    # add nodes
    for node in graph.nodes():
        net.add_node(node, label=str(node))

    # add edges
    for (u, v), val in cum_obstruction.items():
        # compute color
        rgba = yellow_red(norm(val))
        r, g, b = [int(255 * rgba[i]) for i in range(3)]
        color = f"rgb({r}, {g}, {b})"  # full opacity
        # compute width
        width = min_edge_width + (max_edge_width - min_edge_width) * norm(val)
        net.add_edge(u, v, color=color, width=width, title=f"obstruction: {val:.2f}", arrows="to")

    net.write_html(output_file)
    webbrowser.open(f"file://{os.path.abspath(output_file)}")
