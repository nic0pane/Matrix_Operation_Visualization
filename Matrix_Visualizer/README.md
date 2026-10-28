# Matrix Visualizer

A Tkinter desktop application completed from the five supplied source modules.
Python 3.10 or newer is recommended. All source code and tests are included.

## Assessment and provenance

The attached originals were operations-5.py, elimination-4.py,
determinant-3.py, window-2.py and coordinate_grid.py. No main.py,
matrix_input.py, transformations.py or preexisting tests were attached.
All five raw original files parse as Python: the retrieved text preview lost
indentation and some punctuation, so its apparent syntax errors were not
errors in the raw files. The changes address integration and behavior:

- Preserve the original list-comprehension arithmetic, transpose, partial-pivot
  Gaussian / Gauss-Jordan elimination, pivot-count rank, augmented inverse,
  and direct 2x2 / elimination-based larger determinant algorithms.
- Preserve NumPy eig for eigen decomposition, now called once for paired output.
  No arithmetic, determinant, rank, inverse or row reduction was replaced by a
  NumPy solver. Tests do use NumPy as an independent numerical reference.
- Replace printed steps with independent structured snapshots; matrix_display
  returns a string rather than printing.
- Validate non-finite entries and scalars, dimensions, and direct eliminate calls.
- Fix the small-factor skip bug: a small elimination factor can have a large
  effect in another column. Do not erase small entries of the computed inverse.
- Remove the duplicated window creation, module-import window/mainloop, and
  random-scatter demo in window-2.py.
- Replace standalone pyplot figures and savefig return values with reusable
  drawing functions and a single embedded Tk canvas.
- Normalize modules to package paths, using relative imports within packages.

## Setup

Run these commands in the extracted matrix_visualizer directory:

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate on macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies and launch:

```bash
python -m pip install -r requirements.txt
python -m tkinter
python main.py
```

The tkinter command is an optional installation/display check; close its small
window before launching the app. Tkinter is an OS/Python component, not a pip
requirement. If it is missing, install a Python build with Tcl/Tk support.
On Debian/Ubuntu's system Python this is commonly `sudo apt install python3-tk`.
A graphical desktop/display is required. Do not force MPLBACKEND=Agg for the app.

## Use

1. Edit A and B independently. Set Rows / Columns and press Resize or Enter;
   spin arrows also resize. Existing overlapping entries are kept and new
   entries start at zero. Inputs scroll when larger than the available panel.
2. Enter finite real numbers using a decimal point (scientific notation works).
   Clear deliberately leaves blank cells; fill them before using that matrix.
3. Choose an operation. Binary operations always use A and B. Other operations
   use only the selected A/B target; the scalar is read only for scalar multiplication.
4. Press Calculate. Read Results / Explanation or open Calculation steps.
   Previous / Next walk through snapshots, including augmented inverse steps.
5. Plots update within the same canvas. The toolbar provides pan/zoom/home.
6. Examples include shear/scale, reflection, singularity, complex eigenvalues,
   rectangular matrices, and a 3x3 elimination example.

Changing inputs or loading an example does not silently recompute results:
press Calculate. Errors clear the old numerical result, steps and plot, and
leave the application ready for another calculation. A plotting failure does
not hide an otherwise successful numerical result.

## Architecture

main.py imports GUI startup only within main(), protected by a main guard.
gui/matrix_input.py handles editable grids, dimensions, and numeric parsing.
gui/controller.py lazily reads exactly the inputs needed, calls the backend,
and produces an Outcome for presentation. This dispatch can be tested without Tk.
gui/window.py displays the Outcome, provides step navigation, and owns the
single Figure and FigureCanvasTkAgg.
matrix/ contains only math, validation, formatting and calculation data.
visualization/ receives a Figure and data, clears/draws it, and never calls
pyplot, Tkinter, show(), savefig() or a mainloop.

## Backend API

Existing ordinary returns are preserved:

```python
from matrix.elimination import eliminate, gaussian_elimination, matrix_inverse
from matrix.determinant import matrix_determinant

upper, swaps, pivot_columns = eliminate([[1, 2], [3, 4]])
inverse = matrix_inverse([[1, 2], [3, 4]])
determinant = matrix_determinant([[1, 2], [3, 4]])

calculation = gaussian_elimination([[1, 2], [3, 4]], record_steps=True)
result_matrix = calculation.value
for step in calculation.steps:
    description = step.description
    independent_matrix_snapshot = step.matrix
```

record_steps=True returns CalculationResult(value, steps). The value is exactly
the normal return type; for eliminate it is the original three-item tuple.
For determinant and rank it is a scalar; for row reduction and inversion a matrix.
Every step has its own matrix and row lists, not references to mutable inputs,
other steps, or the final result. The final inverse-extraction step shows the
inverse alone, while earlier inverse steps show the full augmented matrix.

Legacy verbose=True is supported as an alias for returning CalculationResult;
it no longer prints or returns just the unwrapped value. All included callers
use the documented API. matrix_display(matrix, title) now returns a string.
The old eigen_values / eigen_vectors helpers remain available; use
`eigen_decomposition` when eigenvalue/eigenvector pairings matter.

## Geometry

Points are column vectors: transformed points are M @ points. Gray dashed grid,
basis and unit square show the original geometry; blue shows the transformed
geometry with equal x/y scaling. Matrix multiplication overlays purple B-stage
geometry and blue AB-stage geometry: (AB)v = A(Bv), so B acts first.
If A or B has a non-2D intermediate space, only a resulting 2x2 product is
plotted as its own map, with a numerical explanation of the distinction.

Determinant plots show the transformed square's area factor abs(det), orientation
preservation/reversal and singular collapse. Real 2x2 eigenvector plots show
paired directions and Mv = lambda*v. Complex values and vectors are printed
with imaginary components intact; their real-2D arrow plot is explicitly
unavailable. Geometric views are not forced onto other sizes or row operations.

## Tests

From the extracted project directory:

```bash
python -m unittest discover -s tests -v
```

No pytest dependency is needed. On a desktop with Tk support, the suite includes
a window smoke test for construction, unused-input validation, recovery after
an error, step navigation, resizing, and canvas reuse. It skips explicitly if
Tkinter or a display is unavailable.

Tests cover arithmetic, incompatible dimensions, malformed and non-finite
entries, determinants, singular and invertible matrices, rectangular elimination,
RREF, rank, pivot-limit validation, recording, independent snapshots, preserving
inputs, silent legacy calls, real/complex eigenpair residuals, and plotting.
Dispatch integration tests verify that determinant(A) never reads invalid B or
an irrelevant scalar. Non-interactive rendering tests use FigureCanvasAgg,
not Tk, and assert column-vector transformation geometry and canvas clearing.

See VERIFICATION.txt for the actual environment and execution results.
No preexisting test files were supplied to preserve.

## Remaining limitations

- The implementation was tested without a GUI display; live desktop behavior
  still requires verification on the user's system. The Tk smoke test is included.
- GUI input dimensions are limited to 1..20 to keep manual entry and snapshot
  storage usable. The backend has no such fixed size limit.
- Input matrices must be finite real lists/tuples; complex eigen results are
  supported, but general complex matrix input is not. Decimal commas and
  fraction expressions are not parsed.
- Floating-point arithmetic is approximate. The original absolute pivot tolerance
  EPS=1e-12 is retained for elimination, rank, inverse and larger determinants.
  Ill-scaled or nearly singular matrices can therefore be treated as rank
  deficient. This is not a symbolic/exact-arithmetic or condition-number tool.
  The retained direct 1x1/2x2 determinant formulas do not apply a pivot cutoff,
  so a tiny nonzero determinant can coexist with an inverse rejected at tolerance.
- Numerical display uses six significant digits; recorded snapshots retain the
  underlying precision. Very large drawable values (above 1e100) are declined
  rather than producing a broken plot. Finite extreme arithmetic may overflow;
  the UI reports numeric errors rather than terminating.
- Highly anisotropic transforms can make small features hard to see on an equal
  scale. Zero transformed vectors have zero-length arrows; their labels remain.
- Repeated eigenvalues may have dependent eigenvectors. There is no guarantee
  that all eigenvectors constitute an independent basis for a defective matrix.
- Calculations run synchronously. Snapshot history uses memory proportional to
  the number of steps times the matrix size; there are no background workers,
  animated transforms, file persistence, or 3D geometric views.
