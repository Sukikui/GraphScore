from pathlib import Path

import click

from metrics import (
    add_max_cumulative_obstruction,
    compute_mastora,
    compute_qanadli,
    visualize_cumulative_obstruction_pyvis,
    visualize_graph_plotly,
)
from tree import json_to_directed_graph


@click.group()
def main() -> None:
    """GraphScore CLI for computing and visualizing pulmonary embolism risk scores."""


@click.command()
@click.argument(
    "input_file",
    type=str,
)
@click.option(
    "--obstruction-attr",
    type=str,
    default="max_transversal_obstruction",
    show_default=True,
    help="The edge attribute to use for obstruction values.",
)
def visualize(input_file: str, obstruction_attr: str) -> None:
    """Visualize cumulative obstruction from a graph JSON file.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
    """
    input_file_path = get_full_file_path(Path(input_file))
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    click.echo("Computing cumulative obstruction...")
    new_graph = add_max_cumulative_obstruction(graph)
    click.echo("Creating visualization...")
    visualize_graph_plotly(new_graph, obstruction_attr=obstruction_attr)


@click.command()
@click.argument(
    "input_file",
    type=str,
)
@click.option(
    "--use-percentage",
    is_flag=True,
    default=False,
    help="If set, treat degrees as obstruction percentages (0 to 1). Otherwise, use degrees (0 to 5).",
)
@click.option(
    "--mode",
    type=str,
    default="mls",
    show_default=True,
    help="Artery levels to include: 'm' (mediastinal), 'l' (lobar), 's' (segmental). Any combination (e.g., 'mls').",
)
@click.option(
    "--obstruction-attr",
    type=str,
    default="max_transversal_obstruction",
    show_default=True,
    help="The edge attribute to use for obstruction values.",
)
def mastora(input_file: str, use_percentage: bool, mode: str, obstruction_attr: str) -> None:
    """Compute Mastora score from a graph JSON file.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
    """
    input_file_path = get_full_file_path(Path(input_file))
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    new_graph = add_max_cumulative_obstruction(graph)
    click.echo("Computing Mastora score...")
    score = compute_mastora(
        new_graph, 
        use_percentage=use_percentage, 
        mode=mode,
        obstruction_attr=obstruction_attr
    )
    click.echo(f"Mastora score: {score}")


@click.command()
@click.argument(
    "input_file",
    type=str,
)
@click.option(
    "--min-obstruction-thresh",
    type=float,
    default=0.25,
    show_default=True,
    help="Minimum obstruction threshold for considering a segment.",
)
@click.option(
    "--max-obstruction-thresh",
    type=float,
    default=0.75,
    show_default=True,
    help="Maximum obstruction threshold for considering a segment.",
)
@click.option(
    "--obstruction-attr",
    type=str,
    default="max_transversal_obstruction",
    show_default=True,
    help="The edge attribute to use for obstruction values.",
)
def qanadli(input_file: str, min_obstruction_thresh: float, max_obstruction_thresh: float, obstruction_attr: str) -> None:
    """Compute Qanadli score from a graph JSON file.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
    """
    input_file_path = get_full_file_path(Path(input_file))
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    new_graph = add_max_cumulative_obstruction(graph)
    click.echo("Computing Qanadli score...")
    score = compute_qanadli(
        new_graph, 
        min_obstruction_thresh=min_obstruction_thresh, 
        max_obstruction_thresh=max_obstruction_thresh,
        obstruction_attr=obstruction_attr
    )
    click.echo(f"Qanadli score: {score}")


@click.command()
@click.argument(
    "input_file",
    type=str,
)
@click.option(
    "--output-file",
    type=str,
    default="data/pyvis/graph_obstruction.html",
    show_default=True,
    help="Output HTML file path.",
)
@click.option(
    "--obstruction-attr",
    type=str,
    default="max_transversal_obstruction",
    show_default=True,
    help="The edge attribute to use for obstruction values.",
)
def visualize_pyvis(input_file: str, output_file: str, obstruction_attr: str) -> None:
    """Visualize cumulative obstruction from a graph JSON file using PyVis network visualization.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
    """
    input_file_path = get_full_file_path(Path(input_file))
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    click.echo("Computing cumulative obstruction...")
    new_graph = add_max_cumulative_obstruction(graph)
    click.echo("Creating interactive visualization...")
    visualize_cumulative_obstruction_pyvis(
        new_graph, 
        obstruction_attr=obstruction_attr,
        output_file=output_file
    )
    click.echo(f"Visualization saved to {output_file}")


def get_full_file_path(input_file: Path) -> Path:
    """Get full file path for the input file."""
    if input_file.is_file():
        return input_file
    # Assuming the input is a patient ID, construct the path with a 4-digit format
    patient_id = input_file.stem.zfill(4)
    constructed_path = Path(f"../data/graphs/{patient_id}_graph_ep_transversal_obstruction.json")

    # Check if the constructed path exists
    if constructed_path.is_file():
        return constructed_path
    # Try with current directory as well
    alt_path = Path(f"data/graphs/{patient_id}_graph_ep_transversal_obstruction.json")
    if alt_path.is_file():
        return alt_path
    raise FileNotFoundError(
        f"Could not find file for patient ID '{patient_id}'. Tried: {constructed_path} and {alt_path}"
    )


if __name__ == "__main__":
    main()
