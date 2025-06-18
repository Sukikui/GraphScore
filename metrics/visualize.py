import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import networkx as nx
from matplotlib.colors import LinearSegmentedColormap, Normalize
from pyvis.network import Network


def visualize_cumulative_obstruction_pyvis(
    graph: nx.DiGraph,
    obstruction_attr: str = "cumulative_max_transversal_obstruction",
    use_hierarchical: bool = True,
    height: str = "1400px",
    width: str = "100%",
    bgcolor: str = "#000000",
    font_color: str = "#ffffff",
    min_edge_width: float = 1.0,
    max_edge_width: float = 5.0,
) -> None:
    """Visualizes a directed graph with obstruction values using PyVis.

    Creates a temporary HTTP server to render the graph visualization in a web browser.
    Graph edges are colored based on their obstruction values using a yellow-to-red
    colormap. Node layout can be hierarchical or force-directed.

    Args:
        graph: A NetworkX directed graph to visualize.
        obstruction_attr: The edge attribute name containing obstruction values.
        use_hierarchical: Whether to use hierarchical layout (True) or force-directed layout (False).
        height: Height of the visualization container.
        width: Width of the visualization container.
        bgcolor: Background color in hex format.
        font_color: Font color in hex format.
        min_edge_width: Minimum edge width for edges with lowest obstruction.
        max_edge_width: Maximum edge width for edges with highest obstruction.

    Returns:
        None. Opens the visualization in the default web browser.

    Note:
        Volatile in-memory PyVis render via a one-shot HTTP server:
        - no lib/ folder, no on-disk HTML
        - blocks only until the browser has fetched the page
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

    vals = [data.get(obstruction_attr, 0.0) for _, _, data in graph.edges(data=True)]
    norm = Normalize(vmin=min(vals, default=0.0), vmax=max(vals, default=1.0) or 1.0)
    cmap = LinearSegmentedColormap.from_list("yr", ["#ffff00", "#ff0000"])
    for u, v, data in graph.edges(data=True):
        val = data.get(obstruction_attr, 0.0)
        r, g, b, _ = cmap(norm(val))
        color = f"rgb({int(255 * r)},{int(255 * g)},{int(255 * b)})"
        width = min_edge_width + (max_edge_width - min_edge_width) * norm(val)
        net.add_edge(u, v, color=color, width=width, title=f"{obstruction_attr}: {val:.2f}", arrows="to")

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
    webbrowser.open(f"http://{host}:{port}")
    server.handle_request()
