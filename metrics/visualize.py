import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import networkx as nx
from matplotlib.colors import LinearSegmentedColormap, Normalize
from pyvis.network import Network


def visualize_cumulative_obstruction_pyvis(
    graph: nx.DiGraph,
    obstruction_attr: str = "cumulative_max_transversal_obstruction",
    level_attr: str = "level",
    use_hierarchical: bool = True,
    height: str = "1400px",
    width: str = "100%",
    bgcolor: str = "#000000",
    font_color: str = "#ffffff",
    min_edge_width: float = 0.2,
    max_edge_width: float = 20.0,
) -> None:
    """Visualizes a directed graph with obstruction values using PyVis.

    Creates a temporary HTTP server to render the graph visualization in a web browser.
    Graph edges are colored based on their obstruction values using a yellow-to-red
    colormap and sized (inversely) based on their `level` attribute.
    Node layout can be hierarchical or force-directed.

    Args:
        graph: A NetworkX directed graph to visualize.
        obstruction_attr: The edge attribute name containing obstruction values.
        level_attr: The edge attribute name containing level values (for width).
        use_hierarchical: Whether to use hierarchical layout (True) or force-directed layout (False).
        height: Height of the visualization container.
        width: Width of the visualization container.
        bgcolor: Background color in hex format.
        font_color: Font color in hex format.
        min_edge_width: Minimum edge width for highest levels.
        max_edge_width: Maximum edge width for lowest levels.

    Returns:
        None. Opens the visualization in the default web browser.
    """
    net = Network(
        height=height,
        width=width,
        bgcolor=bgcolor,
        font_color=font_color,
        directed=True,
        notebook=False,
        cdn_resources="remote",
    )
    net.toggle_physics(False)
    if use_hierarchical:
        net.set_options("""
        {
          "layout": { "hierarchical": {
            "enabled": true,
            "direction": "UD",
            "levelSeparation": 200,
            "nodeSpacing": 150,
            "treeSpacing": 300
          }},
          "physics": { "enabled": false }
        }
        """)
    for n in graph.nodes():
        net.add_node(n, label=str(n))

    # prepare color map for obstruction
    obs_vals = [data.get(obstruction_attr, 0.0) for _, _, data in graph.edges(data=True)]
    obs_norm = Normalize(vmin=min(obs_vals, default=0.0), vmax=max(obs_vals, default=1.0) or 1.0)
    cmap = LinearSegmentedColormap.from_list("bpr", ["#aaaaff", "#ff00ff", "#ff0000"])

    # prepare normalizer for level → width (inverted)
    lvl_vals = [data.get(level_attr, 0.0) for _, _, data in graph.edges(data=True)]
    lvl_norm = Normalize(vmin=min(lvl_vals, default=0.0), vmax=max(lvl_vals, default=1.0) or 1.0)

    for u, v, data in graph.edges(data=True):
        # color by obstruction
        obs = data.get(obstruction_attr, 0.0)
        r, g, b, _ = cmap(obs_norm(obs))
        color = f"rgb({int(255 * r)},{int(255 * g)},{int(255 * b)})"

        # width inversely by level: smaller level → thicker edge
        lvl = data.get(level_attr, 0.0)
        inv = 1.0 - lvl_norm(lvl)
        width = min_edge_width + (max_edge_width - min_edge_width) * inv

        net.add_edge(
            u,
            v,
            color=color,
            width=width,
            title=f"{obstruction_attr}: {obs:.2f}<br>{level_attr}: {lvl}",
            arrows="to",
        )

    # generate HTML bytes
    html_bytes = net.generate_html().encode("utf-8")

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)

        def log_message(self, *args) -> None:
            pass  # silence access logs

    # bind to localhost on an ephemeral port
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    host, port = server.server_address

    # open the page and block until one request is served
    webbrowser.open(f"http://{host}:{port}")
    server.handle_request()
