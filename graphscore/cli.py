from pathlib import Path

import click

from metrics import (
    compute_mastora,
    compute_qanadli,
    visualize_cumulative_obstruction_pyvis,
)
from tree import add_max_cumulative_obstruction, directed_graph_to_json, json_to_directed_graph


@click.command()
@click.argument(
    "input_file",
    type=str,
)
@click.option(
    "--use-percentage",
    "-p",
    is_flag=True,
    default=False,
    help="If set, treat degrees as obstruction percentages (0 to 1). Otherwise, use degrees (0 to 5).",
)
@click.option(
    "--mode",
    "-m",
    type=str,
    default="mls",
    show_default=True,
    help="Artery levels to include: 'm' (mediastinal), 'l' (lobar), 's' (segmental). Any combination (e.g., 'mls').",
)
@click.option(
    "--obstruction-attr",
    "-o",
    type=str,
    default="max_transversal_obstruction",
    show_default=True,
    help="The edge attribute to use for obstruction values.",
)
def mastora(input_file: str, use_percentage: bool, mode: str, obstruction_attr: str) -> None:
    """Compute Mastora score from a graph JSON file.

    Calculates the Mastora score for pulmonary embolism risk assessment, which evaluates
    the degree of vascular obstruction in mediastinal, lobar, and segmental arteries.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
    """
    input_file_path = get_full_file_path(Path(input_file))
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    new_graph = add_max_cumulative_obstruction(graph)
    click.echo("Computing Mastora score...")
    score = compute_mastora(new_graph, use_percentage=use_percentage, mode=mode, obstruction_attr=obstruction_attr)
    click.echo(f"Mastora score: {score}")


@click.command()
@click.argument(
    "input_file",
    type=str,
)
@click.option(
    "--min-obstruction-thresh",
    "-n",
    type=float,
    default=0.25,
    show_default=True,
    help="Minimum obstruction threshold for considering a segment.",
)
@click.option(
    "--max-obstruction-thresh",
    "-x",
    type=float,
    default=0.75,
    show_default=True,
    help="Maximum obstruction threshold for considering a segment.",
)
@click.option(
    "--obstruction-attr",
    "-o",
    type=str,
    default="max_transversal_obstruction",
    show_default=True,
    help="The edge attribute to use for obstruction values.",
)
def qanadli(
    input_file: str, min_obstruction_thresh: float, max_obstruction_thresh: float, obstruction_attr: str
) -> None:
    """Compute Qanadli score from a graph JSON file.

    Calculates the Qanadli score for pulmonary embolism risk assessment, which considers
    both the location of emboli and the degree of obstruction, weighting each segment
    by the number of distal subsegments it supplies.

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
        obstruction_attr=obstruction_attr,
    )
    click.echo(f"Qanadli score: {score}")


@click.command()
@click.argument(
    "input_file",
    type=str,
)
@click.option(
    "--obstruction-attr",
    "-o",
    type=str,
    default="max_transversal_obstruction",
    show_default=True,
    help="The edge attribute to use for obstruction values.",
)
def visualize(input_file: str, obstruction_attr: str) -> None:
    """Visualize cumulative obstruction from a graph JSON file using PyVis network visualization.

    Creates an interactive network visualization of the arterial tree with edges colored
    based on obstruction values. The visualization is displayed in a web browser.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
    """
    input_file_path = get_full_file_path(Path(input_file))
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    click.echo("Computing cumulative obstruction...")
    new_graph = add_max_cumulative_obstruction(graph)
    click.echo("Creating interactive visualization...")
    visualize_cumulative_obstruction_pyvis(new_graph, obstruction_attr=obstruction_attr)
    click.echo("Visualization created. Open the browser to view it.")


def get_full_file_path(input_file: Path) -> Path:
    """Get full file path for the input file.

    Resolves either a direct file path or a patient ID to a complete file path. If a patient ID is provided, it is zero-
    padded to 4 digits and resolved to the standard file naming convention in the data/graphs directory.
    """
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


@click.command()
@click.argument(
    "input_file",
    type=str,
    required=False,
)
@click.option(
    "--output-dir",
    "-d",
    type=str,
    default="data/cumulative_graphs/",
    show_default=True,
    help="Directory where to save the cumulative graph files.",
)
def generate_cumulative(input_file: str | None = None, output_dir: str = "data/cumulative_graphs/") -> None:
    """Generate cumulative obstruction graph from a JSON file and save it.

    Takes an arterial tree graph, processes it to add cumulative obstruction values,
    and saves the resulting graph to the specified output directory.

    INPUT_FILE: Input JSON graph, indicate full file path or only patient ID (e.g., 0055).
                If not provided, processes all graphs in the data/graphs directory.
    """
    output_dir_path = Path(output_dir)

    # Process all graphs if no input file is specified
    if input_file is None:
        graphs_dir = Path("data/graphs/")
        if not graphs_dir.exists():
            graphs_dir = Path("../data/graphs/")
            if not graphs_dir.exists():
                raise FileNotFoundError("Could not find graphs directory at data/graphs/ or ../data/graphs/")

        graph_files = list(graphs_dir.glob("*_graph_ep_transversal_obstruction.json"))
        if not graph_files:
            click.echo(f"No graph files found in {graphs_dir}")
            return

        click.echo(f"Found {len(graph_files)} graph files to process")
        for graph_file in graph_files:
            process_single_graph(graph_file, output_dir_path)
        click.echo(f"All graphs processed and saved to {output_dir_path}")
    else:
        # Process a single graph
        input_file_path = get_full_file_path(Path(input_file))
        process_single_graph(input_file_path, output_dir_path)


def process_single_graph(input_file_path: Path, output_dir_path: Path) -> None:
    """Process a single graph file, adding cumulative obstruction and saving the result.

    Args:
        input_file_path: Path to the input graph file
        output_dir_path: Directory where to save the output
    """
    click.echo(f"Loading graph from {input_file_path}")
    graph = json_to_directed_graph(input_file_path)
    click.echo("Computing cumulative obstruction...")
    new_graph = add_max_cumulative_obstruction(graph)

    # Generate output filename
    output_filename = f"{input_file_path.stem}_cumulative.json"
    output_path = output_dir_path / output_filename

    # Save graph to JSON file
    directed_graph_to_json(new_graph, output_path)
    click.echo(f"Cumulative graph saved to {output_path}")
