from pathlib import Path

import click
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from scipy.stats import pearsonr

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
    score_name: str, clinical_data: pd.DataFrame, graphs_dir: Path, obstruction_attr: str, all_attributes: bool = False
) -> pd.DataFrame:
    """Calculate scores for each patient in the clinical data.

    Args:
        score_name: The name of the score to calculate ('mastora' or 'qanadli').
        clinical_data: DataFrame with clinical data.
        graphs_dir: The path to the directory containing graph files.
        obstruction_attr: The edge attribute to use for obstruction values.
        all_attributes: If True, calculate scores for all obstruction attributes.

    Returns:
        A pandas DataFrame with patient IDs, clinical attributes, and calculated scores.
    """
    if all_attributes:
        all_attrs = [
            "max_transversal_obstruction",
            "max_transversal_obstruction_propagated",
            "max_transversal_obstruction_cumulated",
        ]
        all_scores = []
        all_patient_ids = []
        all_attr_names = []

        for attr in all_attrs:
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
                        score = compute_mastora(new_graph, obstruction_attr=attr)
                    elif score_name == "qanadli":
                        score = compute_qanadli(new_graph, obstruction_attr=attr)
                    else:
                        raise ValueError(f"Invalid score name: {score_name}")

                    all_scores.append(score)
                    all_patient_ids.append(patient_id)
                    all_attr_names.append(attr)

                except Exception as e:
                    click.echo(f"Could not process graph for patient {patient_id_str} with attr {attr}: {e}", err=True)

        score_df = pd.DataFrame(
            {"patient_id": all_patient_ids, "score": all_scores, "obstruction_attr": all_attr_names}
        )
        return pd.merge(clinical_data, score_df, on="patient_id")

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
                raise ValueError(f"Invalid score name: {score_name}")

            scores.append(score)
            patient_ids_with_scores.append(patient_id)

        except Exception as e:
            click.echo(f"Could not process graph for patient {patient_id_str}: {e}", err=True)

    score_df = pd.DataFrame({"patient_id": patient_ids_with_scores, "score": scores})
    return pd.merge(clinical_data, score_df, on="patient_id")


def calculate_pearson_correlation(data: pd.DataFrame, score_col: str, attribute_col: str) -> tuple[float, float]:
    """Calculate Pearson correlation coefficient and p-value.

    Args:
        data: DataFrame with score and attribute data
        score_col: Column name for scores
        attribute_col: Column name for clinical attribute

    Returns:
        Tuple of (correlation_coefficient, p_value)
    """
    # Remove any rows with NaN values
    clean_data = data[[score_col, attribute_col]].dropna()

    if len(clean_data) < 2:
        return float("nan"), float("nan")

    correlation, p_value = pearsonr(clean_data[score_col], clean_data[attribute_col])
    return correlation, p_value


def plot_correlation(
    data: pd.DataFrame,
    score_name: str,
    attribute: str,
    clinical_data_path: str,
    graphs_dir_path: str,
    obstruction_attr: str,
    cli_command: str,
    all_attributes: bool = False,
    show_visualization: bool = False,
) -> None:
    """Plot the correlation using Plotly and display it.

    Args:
        data: DataFrame containing the data to plot.
        score_name: The name of the score.
        attribute: The clinical attribute.
        clinical_data_path: The path to the clinical data file.
        graphs_dir_path: The path to the directory with graph files.
        obstruction_attr: The edge attribute for obstruction values.
        cli_command: The CLI command used to run this function, for display in the plot title.
        all_attributes: If True, create subplots for each obstruction attribute with color coding by patient ID.
        show_visualization: If True, display the correlation plot visualization in browser.
    """
    # Set plotly to use browser renderer
    pio.renderers.default = "browser"

    if all_attributes:
        # Get unique obstruction attributes
        unique_attrs = data["obstruction_attr"].unique()
        n_attrs = len(unique_attrs)

        # Create subplots - arrange in a row
        fig = make_subplots(
            rows=1,
            cols=n_attrs,
            subplot_titles=[
                attr.replace("max_transversal_obstruction", "Max Transversal Obstruction")
                .replace("_propagated", " Propagated")
                .replace("_cumulated", " Cumulated")
                for attr in unique_attrs
            ],
            shared_yaxes=True,
            horizontal_spacing=0.08,
        )

        # Generate consistent colors for each patient ID across all subplots
        unique_patient_ids = sorted(data["patient_id"].unique())
        colors = px.colors.qualitative.Dark2[: len(unique_patient_ids)]
        if len(unique_patient_ids) > len(colors):
            colors = colors * (len(unique_patient_ids) // len(colors) + 1)
        patient_color_map = {pid: colors[i] for i, pid in enumerate(unique_patient_ids)}

        # Calculate and display correlation statistics for each attribute
        correlation_stats = {}

        # Add scatter plots for each obstruction attribute
        for i, attr in enumerate(unique_attrs):
            attr_data = data[data["obstruction_attr"] == attr]

            # Calculate and always print correlation for this attribute
            correlation, p_value = calculate_pearson_correlation(attr_data, "score", attribute)
            correlation_stats[attr] = (correlation, p_value)

            # Print correlation statistics
            if not pd.isna(correlation):
                click.echo(f"Pearson correlation for {attr}: r={correlation:.3f}, p={p_value:.3f}")
            else:
                click.echo(f"Pearson correlation for {attr}: insufficient data")

            for patient_id in unique_patient_ids:
                patient_data = attr_data[attr_data["patient_id"] == patient_id]

                if not patient_data.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=patient_data["score"],
                            y=patient_data[attribute],
                            mode="markers",
                            marker={"size": 12, "color": patient_color_map[patient_id], "opacity": 0.75},
                            name=f"Patient {patient_id}",
                            legendgroup=f"patient_{patient_id}",
                            showlegend=i == 0,  # Only show legend for first subplot
                            hovertemplate=f"Patient ID: {patient_id}<br>"
                            f"{score_name.capitalize()} Score: %{{x}}<br>"
                            f"{attribute.capitalize()}: %{{y}}<extra></extra>",
                        ),
                        row=1,
                        col=i + 1,
                    )

        # Update layout
        title_text = (
            f"Correlation between {score_name.capitalize()} Score and {attribute.capitalize()}<br>"
            f"<sup>Clinical Data: <span style='color:blue;'>{clinical_data_path}</span> "
            f"| Graphs Directory: <span style='color:blue;'>{graphs_dir_path}</span>"
            f"<br>CLI Command: <span style='color:green;'>{cli_command}</span></sup>"
        )

        fig.update_layout(
            title=title_text,
            title_font_size=18,
            plot_bgcolor="white",
            showlegend=True,
            legend={"orientation": "v", "yanchor": "top", "y": 1, "xanchor": "left", "x": 1.02},
            height=800,
            margin={"t": 200},
        )

        # Update axes
        for i in range(n_attrs):
            fig.update_xaxes(
                title_text=f"{score_name.capitalize()} Score", showgrid=True, gridcolor="lightgray", row=1, col=i + 1
            )
            if i == 0:  # Only add y-axis title to first subplot
                fig.update_yaxes(
                    title_text=attribute.capitalize(), showgrid=True, gridcolor="lightgray", row=1, col=i + 1
                )
            else:
                fig.update_yaxes(showgrid=True, gridcolor="lightgray", row=1, col=i + 1)

    else:
        # Calculate and always print correlation for single attribute case
        correlation, p_value = calculate_pearson_correlation(data, "score", attribute)
        if not pd.isna(correlation):
            click.echo(f"Pearson correlation: r={correlation:.3f}, p={p_value:.3f}")
        else:
            click.echo("Pearson correlation: insufficient data")

        title_text = (
            f"Correlation between {score_name.capitalize()} Score and {attribute.capitalize()}<br>"
            f"<sup>Clinical Data: <span style='color:blue;'>{clinical_data_path}</span> "
            f"| Graphs Directory: <span style='color:blue;'>{graphs_dir_path}</span> "
            f"| Obstruction Attribute: <span style='color:blue;'>{obstruction_attr}</span>"
            f"<br>CLI Command: <span style='color:green;'>{cli_command}</span></sup>"
        )
        fig = px.scatter(
            data,
            x="score",
            y=attribute,
            title=title_text,
            labels={"score": f"{score_name.capitalize()} Score", attribute: attribute.capitalize()},
            hover_data=["patient_id"],
        )
        fig.update_traces(marker={"size": 20})

        fig.update_layout(
            plot_bgcolor="white",
            xaxis={"showgrid": True, "gridcolor": "lightgray"},
            yaxis={"showgrid": True, "gridcolor": "lightgray"},
            title_font_size=24,
        )

    if show_visualization:
        fig.show()
        click.echo("Correlation plot displayed.")
    else:
        click.echo("Correlation plot not displayed. Use --show-visualization to view plot.")


def correlate_and_plot(
    score_name: str,
    attribute: str,
    clinical_data_path: str,
    graphs_dir_path: str,
    obstruction_attr: str,
    cli_command: str,
    all_attributes: bool = False,
    show_visualization: bool = False,
) -> None:
    """Load data, calculate scores, and plot the correlation.

    Args:
        score_name: The name of the score to calculate.
        attribute: The clinical attribute to correlate against.
        clinical_data_path: The path to the clinical data file.
        graphs_dir_path: The path to the directory with graph files.
        obstruction_attr: The edge attribute for obstruction values.
        cli_command: The CLI command used to run this function, for display in the plot title.
        all_attributes: If True, calculate and plot scores for all obstruction attributes.
        show_visualization: If True, display the correlation plot visualization in browser.
    """
    clinical_path = Path(clinical_data_path)
    graphs_dir = Path(graphs_dir_path)

    click.echo(f"Loading clinical data from {clinical_path}...")
    clinical_df = load_and_clean_clinical_data(clinical_path, attribute)

    if all_attributes:
        click.echo(f"Calculating {score_name} scores for all obstruction attributes...")
    else:
        click.echo(f"Calculating {score_name} scores for patients...")

    data_with_scores = calculate_scores(score_name, clinical_df, graphs_dir, obstruction_attr, all_attributes)

    if data_with_scores.empty:
        click.echo("No data to plot. Make sure graph files exist and patient IDs match.", err=True)
        return

    if show_visualization:
        click.echo("Generating correlation plot...")
    plot_correlation(
        data_with_scores,
        score_name,
        attribute,
        clinical_data_path,
        graphs_dir_path,
        obstruction_attr,
        cli_command,
        all_attributes,
        show_visualization,
    )
