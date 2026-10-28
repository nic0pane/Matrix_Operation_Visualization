import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.patches import Polygon
from matplotlib.ticker import MaxNLocator, ScalarFormatter

FIGURE_BACKGROUND = "#191d25"
AXES_BACKGROUND = "#222833"
TEXT_COLOR = "#e8edf5"
MUTED_TEXT_COLOR = "#aab7c9"
GRID_COLOR = "#8392a8"
FIRST_VECTOR_COLOR = "#58b9ff"
SECOND_VECTOR_COLOR = "#ffbf69"
ORIGINAL_COLOR = "#aab7c9"
TRANSFORMED_COLOR = "#58b9ff"
INTERMEDIATE_COLOR = "#bd9bff"


def prepare_figure(figure):
    #Reset and style this figure without changing global Matplotlib settings.
    figure.clear()
    figure.set_facecolor(FIGURE_BACKGROUND)
    figure.set_edgecolor(FIGURE_BACKGROUND)


def draw_vector(axes, vector, label, color, *, dashed=False, label_offset=(9, 12)):
    #Draw a vector with a screen-sized arrowhead and a readable label.
    vector_coordinates = np.asarray(vector, dtype=float)
    axes.annotate(
        "",
        xy=vector_coordinates,
        xytext=(0, 0),
        arrowprops={
            "arrowstyle": "-|>",
            "color": color,
            "linewidth": 2.4,
            "linestyle": "--" if dashed else "-",
            "mutation_scale": 15,
            "shrinkA": 0,
            "shrinkB": 0,
        },
        zorder=6,
    )
    axes.annotate(
        label,
        xy=vector_coordinates,
        xytext=label_offset,
        textcoords="offset points",
        color=color,
        fontsize=9,
        fontweight="medium",
        bbox={
            "boxstyle": "round,pad=0.3",
            "facecolor": AXES_BACKGROUND,
            "edgecolor": "none",
            "alpha": 0.92,
        },
        annotation_clip=True,
        zorder=8,
    )


def draw_objects(ax, matrix, color, label, *, original=False):
    """Draw a transformed unit square and basis vectors; return its vertices.

    Keep the original calling signature so the existing GUI needs no changes.
    Bounds now follow the unit square, not an oversized transformed viewport.
    """
    axes = ax
    transformation_matrix = np.asarray(matrix, dtype=float)
    unit_square_vertices = np.array(
        [[0, 1, 1, 0], [0, 0, 1, 1]], dtype=float
    )
    transformed_vertices = transformation_matrix @ unit_square_vertices

    # A small internal mesh communicates shear without overwhelming the arrows.
    for grid_coordinate in (0.25, 0.5, 0.75):
        vertical_endpoints = np.array([[grid_coordinate, grid_coordinate], [0, 1]])
        horizontal_endpoints = np.array([[0, 1], [grid_coordinate, grid_coordinate]])
        for line_endpoints in (vertical_endpoints, horizontal_endpoints):
            transformed_endpoints = transformation_matrix @ line_endpoints
            axes.plot(
                *transformed_endpoints,
                color=color,
                alpha=0.28,
                linewidth=0.8,
                zorder=2,
            )

    axes.add_patch(
        Polygon(
            transformed_vertices.T,
            closed=True,
            facecolor=to_rgba(color, 0.13),
            edgecolor=to_rgba(color, 0.85),
            linewidth=1.7,
            linestyle="--" if original else "-",
            label=label + " unit square",
            zorder=3,
        )
    )

    vector_colors = (FIRST_VECTOR_COLOR, SECOND_VECTOR_COLOR)
    label_offsets = ((9, 12), (9, -23))
    for basis_vector_index, vector_color in enumerate(vector_colors):
        vector_label = (
            f"e{basis_vector_index + 1}"
            if original else f"M e{basis_vector_index + 1}"
        )
        draw_vector(
            axes,
            transformation_matrix[:, basis_vector_index],
            vector_label,
            vector_color,
            label_offset=label_offsets[basis_vector_index],
        )
    axes.scatter([0], [0], s=18, color=TEXT_COLOR, zorder=7)
    return transformed_vertices


def finish_axes(ax, points, title):
    #Fit the actual geometry, retain equal x/y units, and style the axes."""
    axes = ax
    combined_points = np.concatenate(points, axis=1)
    if not np.isfinite(combined_points).all():
        raise ValueError("Plot geometry contains non-finite coordinates")

    minimum_coordinates = np.min(combined_points, axis=1)
    maximum_coordinates = np.max(combined_points, axis=1)
    coordinate_spans = maximum_coordinates - minimum_coordinates
    largest_span = float(np.max(coordinate_spans))
    if largest_span == 0:
        largest_span = 1.0

    # Pad both directions enough for arrow labels, including collapsed maps.
    minimum_span = largest_span * 0.45
    horizontal_span = max(float(coordinate_spans[0]), minimum_span)
    vertical_span = max(float(coordinate_spans[1]), minimum_span)
    horizontal_center, vertical_center = (
        minimum_coordinates + coordinate_spans / 2
    )
    axes.set_xlim(
        horizontal_center - horizontal_span * 0.78,
        horizontal_center + horizontal_span * 0.78,
    )
    axes.set_ylim(
        vertical_center - vertical_span * 0.78,
        vertical_center + vertical_span * 0.78,
    )
    axes.set_facecolor(AXES_BACKGROUND)
    axes.set_aspect("equal", adjustable="box")
    axes.set_axisbelow(True)
    axes.grid(color=GRID_COLOR, alpha=0.14, linewidth=0.7)
    axes.axhline(0, color=GRID_COLOR, alpha=0.65, linewidth=0.9, zorder=1)
    axes.axvline(0, color=GRID_COLOR, alpha=0.65, linewidth=0.9, zorder=1)

    for border_name, border in axes.spines.items():
        border.set_visible(border_name in ("left", "bottom"))
        border.set_color(to_rgba(GRID_COLOR, 0.28))
    axes.tick_params(colors=MUTED_TEXT_COLOR, labelsize=8, length=0, pad=7)
    axes.xaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))
    axes.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))
    for coordinate_axis in (axes.xaxis, axes.yaxis):
        formatter = ScalarFormatter(useOffset=False, useMathText=True)
        formatter.set_powerlimits((-3, 4))
        coordinate_axis.set_major_formatter(formatter)
        coordinate_axis.get_offset_text().set_color(MUTED_TEXT_COLOR)
        coordinate_axis.get_offset_text().set_fontsize(8)
    axes.set_xlabel("x", color=MUTED_TEXT_COLOR, fontsize=9, labelpad=7)
    axes.set_ylabel("y", color=MUTED_TEXT_COLOR, fontsize=9, labelpad=7)
    axes.set_title(title, color=TEXT_COLOR, fontsize=11, fontweight="medium", pad=16)
