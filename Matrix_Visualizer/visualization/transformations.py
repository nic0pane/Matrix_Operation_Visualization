import textwrap
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.patches import Polygon
from matplotlib.ticker import MaxNLocator, ScalarFormatter

FIGURE_BACKGROUND = "#191d25"
AXES_BACKGROUND = "#222833"
TEXT_COLOR = "#e8edf5"
MUTED_COLOR = "#aab7c9"
GRID_COLOR = "#8392a8"
VECTOR_COLORS = ("#58b9ff", "#ffbf69")


def _drawable(matrix):
    #Validate a matrix before replacing an existing plot.
    transformation_matrix = np.asarray(matrix, dtype=float)
    if transformation_matrix.shape != (2, 2):
        raise ValueError("A geometric transformation requires a 2x2 matrix")
    if (
        not np.isfinite(transformation_matrix).all()
        or np.max(np.abs(transformation_matrix)) > 1e100
    ):
        raise ValueError("Values are too large for a reliable geometric plot")
    return transformation_matrix


def _create_axes(figure):
    figure.clear()
    figure.set_facecolor(FIGURE_BACKGROUND)
    figure.set_edgecolor(FIGURE_BACKGROUND)
    axes = figure.add_subplot(111)
    axes.set_facecolor(AXES_BACKGROUND)
    return axes


def _draw_vector(axes, vector, label, color, *, dashed=False, offset=(10, 12)):
    axes.annotate(
        "", xy=vector, xytext=(0, 0), zorder=6,
        arrowprops={
            "arrowstyle": "-|>", "color": color, "linewidth": 2.5,
            "linestyle": "--" if dashed else "-",
            "mutation_scale": 16, "shrinkA": 0, "shrinkB": 0,
        },
    )
    axes.annotate(
        label, xy=vector, xytext=offset, textcoords="offset points",
        color=color, fontsize=10, zorder=8,
        bbox={
            "boxstyle": "round,pad=0.3", "facecolor": AXES_BACKGROUND,
            "edgecolor": "none", "alpha": 0.94,
        },
    )


def _finish_plot(figure, axes, point_groups, title, footer):
    #Fit the final geometry with space for labels; preserve equal x/y units.
    points = np.concatenate(point_groups, axis=1)
    if not np.isfinite(points).all():
        raise ValueError("Plot geometry contains non-finite coordinates")
    minimum_coordinates = points.min(axis=1)
    maximum_coordinates = points.max(axis=1)
    coordinate_spans = maximum_coordinates - minimum_coordinates
    largest_span = float(coordinate_spans.max())
    if largest_span == 0:
        largest_span = 1.0
    padded_spans = np.maximum(coordinate_spans, largest_span * 0.45) * 1.6
    center = minimum_coordinates + coordinate_spans / 2
    axes.set_xlim(center[0] - padded_spans[0] / 2, center[0] + padded_spans[0] / 2)
    axes.set_ylim(center[1] - padded_spans[1] / 2, center[1] + padded_spans[1] / 2)
    axes.set_aspect("equal", adjustable="box")
    axes.set_axisbelow(True)
    axes.grid(color=GRID_COLOR, alpha=0.15, linewidth=0.7)
    axes.axhline(0, color=GRID_COLOR, alpha=0.65, linewidth=0.9, zorder=1)
    axes.axvline(0, color=GRID_COLOR, alpha=0.65, linewidth=0.9, zorder=1)
    for border_name, border in axes.spines.items():
        border.set_visible(border_name in ("left", "bottom"))
        border.set_color(to_rgba(GRID_COLOR, 0.3))
    axes.tick_params(colors=MUTED_COLOR, labelsize=9, length=0, pad=7)
    axes.xaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=3))
    axes.yaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=3))
    for coordinate_axis in (axes.xaxis, axes.yaxis):
        formatter = ScalarFormatter(useOffset=False, useMathText=True)
        formatter.set_powerlimits((-3, 4))
        coordinate_axis.set_major_formatter(formatter)
        coordinate_axis.get_offset_text().set_color(MUTED_COLOR)
    axes.set_xlabel("x", color=MUTED_COLOR, fontsize=10, labelpad=8)
    axes.set_ylabel("y", color=MUTED_COLOR, fontsize=10, labelpad=8)
    axes.scatter([0], [0], s=20, color=TEXT_COLOR, zorder=7)

    figure_width, figure_height = figure.get_size_inches()
    title_width = max(24, int(figure_width * 10))
    wrapped_title = "\n".join(
        textwrap.fill(line, width=title_width) for line in title.splitlines()
    )
    wrapped_footer = "\n".join(
        textwrap.fill(line, width=max(28, int(figure_width * 12)))
        for line in footer.splitlines()
    )
    figure.suptitle(wrapped_title, color=TEXT_COLOR, fontsize=12, y=0.97)
    figure.text(
        0.5, 0.025, wrapped_footer, ha="center", va="bottom",
        color=MUTED_COLOR, fontsize=8, linespacing=1.5,
    )
    top_margin = min(0.3, (0.35 + 0.18 * (wrapped_title.count("\n") + 1)) / max(figure_height, 1))
    bottom_margin = min(0.28, (0.2 + 0.15 * (wrapped_footer.count("\n") + 1)) / max(figure_height, 1))
    figure.tight_layout(rect=(0.02, bottom_margin, 0.98, 1 - top_margin))


def plot_message(figure, message):
    axes = _create_axes(figure)
    axes.set_axis_off()
    line_width = max(24, int(figure.get_size_inches()[0] * 10))
    wrapped_message = "\n".join(
        textwrap.fill(line, width=line_width) for line in message.splitlines()
    )
    axes.text(
        0.5, 0.5, wrapped_message, transform=axes.transAxes,
        ha="center", va="center", color=TEXT_COLOR, fontsize=11, linespacing=1.7,
    )
    figure.subplots_adjust(left=0.08, right=0.92, bottom=0.12, top=0.88)


def plot_transformation(figure, matrix, title="Transformation", intermediate=None):

    transformation_matrix = _drawable(matrix)
    axes = _create_axes(figure)
    unit_square_vertices = np.array([[0, 1, 1, 0], [0, 0, 1, 1]], dtype=float)
    final_vertices = transformation_matrix @ unit_square_vertices
    square_color = VECTOR_COLORS[0]
    axes.add_patch(
        Polygon(
            final_vertices.T, closed=True,
            facecolor=to_rgba(square_color, 0.15),
            edgecolor=to_rgba(square_color, 0.85), linewidth=1.8, zorder=3,
        )
    )
    for grid_coordinate in (0.25, 0.5, 0.75):
        line_groups = (
            np.array([[grid_coordinate, grid_coordinate], [0, 1]]),
            np.array([[0, 1], [grid_coordinate, grid_coordinate]]),
        )
        for line_endpoints in line_groups:
            axes.plot(
                *(transformation_matrix @ line_endpoints),
                color=square_color, alpha=0.28, linewidth=0.8, zorder=2,
            )
    for vector_index, vector_color in enumerate(VECTOR_COLORS):
        final_vector = transformation_matrix[:, vector_index]
        coordinate_label = f"({final_vector[0]:.4g}, {final_vector[1]:.4g})"
        _draw_vector(
            axes, final_vector, f"M e{vector_index + 1}\n{coordinate_label}",
            vector_color, offset=(10, 12) if vector_index == 0 else (10, -32),
        )
    if title.startswith("(AB)v = A(Bv):"):
        title = "Final transformation: AB"
    _finish_plot(
        figure, axes, [final_vertices], title,
        "Final result only | Blue: first column | Orange: second column",
    )


def plot_determinant(figure, matrix, determinant):
    _drawable(matrix)
    if determinant == 0:
        orientation = "Singular: the square collapses to a line or point"
    elif determinant > 0:
        orientation = "Orientation preserved"
    else:
        orientation = "Orientation reversed"
    plot_transformation(
        figure, matrix,
        f"Determinant = {determinant:.6g} | Area scale = {abs(determinant):.6g}\n{orientation}",
    )


def plot_eigenvectors(figure, matrix, values, vectors):
    #Show both real eigenpairs together on a single plot.
    transformation_matrix = _drawable(matrix)
    eigenvalues = np.asarray(values)
    eigenvectors = np.asarray(vectors)
    if eigenvalues.shape != (2,) or eigenvectors.shape != (2, 2):
        raise ValueError("A 2x2 eigenvector plot requires two values and two vector columns")
    if not np.isfinite(eigenvalues).all() or not np.isfinite(eigenvectors).all():
        raise ValueError("Eigenvalues and eigenvectors must be finite")
    if np.any(np.imag(eigenvalues) != 0) or np.any(np.imag(eigenvectors) != 0):
        message = (
            "Complex eigenvalues/eigenvectors are displayed numerically.\n"
            "Their eigenvector directions cannot be drawn as real 2D arrows."
        )
        plot_message(figure, message)
        return message
    real_vectors = np.real(eigenvectors)
    transformed_vectors = transformation_matrix @ real_vectors
    if not np.isfinite(transformed_vectors).all() or np.max(np.abs(transformed_vectors)) > 1e100:
        raise ValueError("Transformed eigenvectors are too large for a reliable plot")
    axes = _create_axes(figure)
    visible_points = [np.zeros((2, 1)), real_vectors, transformed_vectors]
    for vector_index, vector_color in enumerate(VECTOR_COLORS):
        _draw_vector(
            axes, real_vectors[:, vector_index], f"v{vector_index + 1}",
            vector_color, dashed=True,
            offset=(-36, -24) if vector_index == 0 else (10, -24),
        )
        _draw_vector(
            axes, transformed_vectors[:, vector_index],
            f"M v{vector_index + 1} (lambda={eigenvalues[vector_index]:.4g})",
            vector_color, offset=(10, 12) if vector_index == 0 else (10, -40),
        )
    _finish_plot(
        figure, axes, visible_points, "Eigenvectors: Mv = lambda v",
        "Dashed: eigenvector v | Solid: transformed vector Mv",
    )
    return "Eigenvectors are columns of V; each pair uses the same color."