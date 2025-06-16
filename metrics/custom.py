import math
import os
import random
import webbrowser
from collections.abc import Callable
from typing import Any

import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_hex
from pyvis.network import Network

pio.renderers.default = "browser"


def compute_cumulative_obstruction(
    graph: nx.DiGraph,
    root: Any = None,
    root_obstruction: float = 0.0,
    input_attr: str = "transversal_obstruction",
    output_attr: str = "cumulative_max_transversal_obstruction",
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
        root_obstruction (float, optional): Initial obstruction value at the root. Defaults to 0.0.
        input_attr (str, optional): Name of the edge attribute with the raw obstruction degree.
            Defaults to "ep_vessels_occupancy".
        output_attr (str, optional): Name for the new edge attribute to store propagated
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
            new_graph.edges[node, child][output_attr] = cum
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


def visualize_cumulative_obstruction_pyvis(
    graph: nx.DiGraph,
    obstruction_attr: str = "cumulative_max_transversal_obstruction",
    height: str = "1400px",
    width: str = "100%",
    bgcolor: str = "#000000",
    font_color: str = "#ffffff",
    min_edge_width: float = 1.0,
    max_edge_width: float = 5.0,
    output_file: str = "data/graph_obstruction.html",
) -> None:
    """Render an interactive HTML visualization of a directed tree.

    Edges are colored from yellow (low obstruction) to red (high obstruction)
    and width proportional to the propagated obstruction stored in `edge_attr`.

    Args:
        graph (nx.DiGraph): Directed tree structure, with each edge carrying
            a float attribute `edge_attr` in [0,1].
        obstruction_attr (str): Name of the edge attribute to use for obstruction values.
                        Defaults to "cumulative_obstruction".
        height (str): Height of the HTML canvas. Defaults to "1400px".
        width (str): Width of the HTML canvas. Defaults to "100%".
        bgcolor (str): Background color. Defaults to black.
        font_color (str): Node label color. Defaults to white.
        min_edge_width (float): Width for edges with zero obstruction. Defaults to 1.0.
        max_edge_width (float): Width for edges with full obstruction. Defaults to 5.0.
        output_file (str): Path to write the HTML file. Defaults to "graph_obstruction.html".
    """
    cum_obstruction = {(u, v): data.get(obstruction_attr, 0.0) for u, v, data in graph.edges(data=True)}
    values = list(cum_obstruction.values())
    vmin, vmax = min(values, default=0.0), max(values, default=1.0)
    norm = Normalize(vmin=vmin, vmax=(vmax or 1.0))
    yellow_red = LinearSegmentedColormap.from_list("yellow_red", ["#ffff00", "#ff0000"])

    # prepare PyVis
    net = Network(height=height, width=width, bgcolor=bgcolor, font_color=font_color, directed=True, notebook=False)
    net.force_atlas_2based()

    # add nodes
    for node in graph.nodes():
        net.add_node(node, label=str(node))

    # add edges
    for (u, v), val in cum_obstruction.items():
        rgba = yellow_red(norm(val))
        r, g, b = [int(255 * rgba[i]) for i in range(3)]
        color = f"rgb({r}, {g}, {b})"
        width = min_edge_width + (max_edge_width - min_edge_width) * norm(val)
        net.add_edge(u, v, color=color, width=width, title=f"{obstruction_attr}: {val:.2f}", arrows="to")

    net.write_html(output_file)
    webbrowser.open(f"file://{os.path.abspath(output_file)}")


def tree_radial_3d_layout(
    graph: nx.DiGraph,
    root: Any = None,
    radius: float = 15,
    level_height: float = 2.0,
    jitter: float = 0.3,
    initial_spread: float = 5 * math.pi,
) -> dict[Any, tuple[float, float, float]]:
    """Compute a radial 3D layout for a directed tree, placing nodes in a circular pattern.

    Args:
        graph (nx.DiGraph): A directed acyclic graph representing a rooted tree.
        root (Any, optional): The root node. If None, a node with in-degree 0 is automatically selected.
        radius (float): Radial distance between parent and children. Defaults to 15.
        level_height (float): Vertical spacing between levels (along Z axis). Defaults to 2.0.
        jitter (float): Amount of vertical randomness to apply (±). Defaults to 0.3.
        initial_spread (float): Angular span (in radians) for children of the root. Defaults to 5π.

    Returns:
        dict[Any, tuple[float, float, float]]: Mapping from each node to its (x, y, z) 3D coordinates.
    """
    if root is None:
        roots = [n for n, deg in graph.in_degree() if deg == 0]
        if len(roots) != 1:
            raise ValueError("Graph must have exactly one root.")
        root = roots[0]

    pos = {}

    def _place(
        node: Any, center: tuple[float, float], angle: float = 0.0, spread: float = initial_spread, depth: int = 0
    ) -> None:
        z = -depth * level_height + random.uniform(-jitter, jitter)  # noqa: S311
        pos[node] = (center[0], center[1], z)
        children = list(graph.successors(node))
        n = len(children)
        if n == 0:
            return
        angle_step = spread / max(n, 1)
        for i, child in enumerate(children):
            theta = angle + i * angle_step - spread / 2 + random.uniform(-0.1, 0.1)  # noqa: S311
            r = radius * (1 + random.uniform(-0.2, 0.2))  # noqa: S311
            x = center[0] + r * math.cos(theta)
            y = center[1] + r * math.sin(theta)
            _place(child, (x, y), theta, spread / n, depth + 1)

    _place(root, (0.0, 0.0))
    return pos


def visualize_graph_plotly(graph: nx.DiGraph, obstruction_attr: str = "cumulative_max_transversal_obstruction") -> None:
    """Render a 3D visualization of a directed tree using Plotly.

    Nodes are positioned with a radial 3D layout. Edges are colored from yellow to red
    depending on the obstruction value (between 0 and 1).

    Args:
        graph (nx.DiGraph): The directed graph to render, with obstruction values on edges.
        obstruction_attr (str): The name of the edge attribute representing obstruction. Defaults to
            "cumulative_max_transversal_obstruction".

    Returns:
        None
    """
    pos_3d = tree_radial_3d_layout(graph)
    edge_values = [graph.edges[u, v].get(obstruction_attr, 0.0) for u, v in graph.edges()]
    norm = Normalize(vmin=min(edge_values, default=0.0), vmax=max(edge_values, default=1.0))
    cmap = cm.get_cmap("YlOrRd")
    edge_traces = []

    for u, v in graph.edges():
        x0, y0, z0 = pos_3d[u]
        x1, y1, z1 = pos_3d[v]
        val = graph.edges[u, v].get(obstruction_attr, 0.0)
        color = to_hex(cmap(norm(val)))
        edge_traces.append(
            go.Scatter3d(
                x=[x0, x1],
                y=[y0, y1],
                z=[z0, z1],
                mode="lines",
                line={"color": color, "width": 4},
                hoverinfo="text",
                text=f"{u} → {v}<br>{obstruction_attr}: {val:.2f}",
                showlegend=False,
            )
        )

    node_x, node_y, node_z = zip(*[pos_3d[n] for n in graph.nodes()], strict=False)
    node_trace = go.Scatter3d(
        x=node_x,
        y=node_y,
        z=node_z,
        mode="markers+text",
        marker={"size": 6, "color": "white"},
        opacity=0.6,
        text=[str(n) for n in graph.nodes()],
        textposition="top center",
        textfont={"size": 7, "color": "white"},
        hoverinfo="text",
        showlegend=False,
    )

    fig = go.Figure(data=[*edge_traces, node_trace])
    fig.update_layout(
        title="3D Tree Layout",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        scene={
            "xaxis": {"showgrid": False, "zeroline": False, "visible": False},
            "yaxis": {"showgrid": False, "zeroline": False, "visible": False},
            "zaxis": {"showgrid": False, "zeroline": False, "visible": False},
            "bgcolor": "black",
        },
    )
    fig.show()
