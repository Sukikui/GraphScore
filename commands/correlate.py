from pathlib import Path

import click
import pandas as pd
import plotly.express as px
import plotly.io as pio

from commands.mastora import compute_mastora
from commands.qanadli import compute_qanadli
from tree import add_max_attribute_values, json_to_directed_graph


def load_and_clean_clinical_data(file_path: Path, attribute: str) -> pd.DataFrame:
    """Load and clean clinical data from a CSV file.

    Args:
        file_path: The path to the clinical data file.
        attribute: The clinical attribute to extract and clean.

    Returns:
        A pandas DataFrame with cleaned clinical data.
    """
    df = pd.read_csv(file_path)
    # The values can be '< 3' or 'NF'
    df[attribute] = df[attribute].astype(str).str.replace(r"<", "").str.strip()
    df[attribute] = pd.to_numeric(df[attribute], errors="coerce")
    df.dropna(subset=[attribute], inplace=True)
    return df


def calculate_scores(
    score_name: str, clinical_data: pd.DataFrame, graphs_dir: Path, obstruction_attr: str
) -> pd.DataFrame:
    """Calculate scores for each patient in the clinical data.

    Args:
        score_name: The name of the score to calculate ('mastora' or 'qanadli').
        clinical_data: DataFrame with clinical data.
        graphs_dir: The path to the directory containing graph files.
        obstruction_attr: The edge attribute to use for obstruction values.

    Returns:
        A pandas DataFrame with patient IDs, clinical attributes, and calculated scores.
    """
    scores = []
    patient_ids_with_scores = []

    for _, row in clinical_data.iterrows():
        patient_id = row["patient_id"]
        patient_id_str = str(patient_id).zfill(4)
        graph_file = graphs_dir / f"{patient_id_str}_graph_ep_transversal_obstruction.json"

        if not graph_file.is_file():
            continue

        try:
            graph = json_to_directed_graph(graph_file)
            new_graph = add_max_attribute_values(graph)

            if score_name == "mastora":
                score = compute_mastora(new_graph, obstruction_attr=obstruction_attr)
            elif score_name == "qanadli":
                score = compute_qanadli(new_graph, obstruction_attr=obstruction_attr)
            else:
                # This case should ideally be handled by Click's choice validation
                raise ValueError(f"Invalid score name: {score_name}")

            scores.append(score)
            patient_ids_with_scores.append(patient_id)

        except Exception as e:
            click.echo(f"Could not process graph for patient {patient_id_str}: {e}", err=True)

    score_df = pd.DataFrame({"patient_id": patient_ids_with_scores, "score": scores})
    return pd.merge(clinical_data, score_df, on="patient_id")


def plot_correlation(data: pd.DataFrame, score_name: str, attribute: str) -> None:
    """Plot the correlation using Plotly and display it.

    Args:
        data: DataFrame containing the data to plot.
        score_name: The name of the score.
        attribute: The clinical attribute.
    """
    # Set plotly to use browser renderer
    pio.renderers.default = "browser"
    fig = px.scatter(
        data,
        x="score",
        y=attribute,
        title=f"Correlation between {score_name.capitalize()} Score and {attribute.capitalize()}",
        labels={"score": f"{score_name.capitalize()} Score", attribute: attribute.capitalize()},
        hover_data=["patient_id"],
    )
    fig.update_traces(marker={"size": 12})
    fig.update_layout(
        plot_bgcolor="white",
        xaxis={"showgrid": True, "gridcolor": "lightgray"},
        yaxis={"showgrid": True, "gridcolor": "lightgray"},
    )
    fig.show()
    click.echo("Correlation plot displayed.")


def correlate_and_plot(
    score_name: str, attribute: str, clinical_data_path: str, graphs_dir_path: str, obstruction_attr: str
) -> None:
    """Load data, calculate scores, and plot the correlation.

    Args:
        score_name: The name of the score to calculate.
        attribute: The clinical attribute to correlate against.
        clinical_data_path: The path to the clinical data file.
        graphs_dir_path: The path to the directory with graph files.
        obstruction_attr: The edge attribute for obstruction values.
    """
    clinical_path = Path(clinical_data_path)
    graphs_dir = Path(graphs_dir_path)

    click.echo(f"Loading clinical data from {clinical_path}...")
    clinical_df = load_and_clean_clinical_data(clinical_path, attribute)

    click.echo(f"Calculating {score_name} scores for patients...")
    data_with_scores = calculate_scores(score_name, clinical_df, graphs_dir, obstruction_attr)

    if data_with_scores.empty:
        click.echo("No data to plot. Make sure graph files exist and patient IDs match.", err=True)
        return

    click.echo("Generating correlation plot...")
    plot_correlation(data_with_scores, score_name, attribute)
