from pathlib import Path

import click

from metrics import add_max_cumulative_obstruction, compute_mastora, compute_qanadli, visualize_graph_plotly
from tree import json_to_directed_graph


@click.group()
def main() -> None:
    """GraphScore CLI for computing and visualizing pulmonary embolism risk scores."""


@click.command()
@click.argument(
    "input_file",
    type=str,
)
def visualize(input_file: str) -> None:
    """Visualize cumulative obstruction from a graph JSON file.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
    """
    input_file_path = get_full_file_path(Path(input_file))
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    click.echo("Computing cumulative obstruction...")
    new_graph = add_max_cumulative_obstruction(graph)
    click.echo("Creating visualization...")
    visualize_graph_plotly(new_graph)


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
def mastora(input_file: str, use_percentage: bool, mode: str) -> None:
    """Compute Mastora score from a graph JSON file.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
    """
    input_file_path = get_full_file_path(Path(input_file))
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    new_graph = add_max_cumulative_obstruction(graph)
    click.echo("Computing Mastora score...")
    score = compute_mastora(new_graph, use_percentage=use_percentage, mode=mode)
    click.echo(f"Mastora score: {score}")


@click.command()
@click.argument(
    "input_file",
    type=str,
)
def qanadli(input_file: str) -> None:
    """Compute Qanadli score from a graph JSON file.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
    """
    input_file_path = get_full_file_path(Path(input_file))
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    new_graph = add_max_cumulative_obstruction(graph)
    click.echo("Computing Qanadli score...")
    score = compute_qanadli(new_graph)
    click.echo(f"Qanadli score: {score}")


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
