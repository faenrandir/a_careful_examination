import numpy as np
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, output_file, show
from sklearn.linear_model import LinearRegression

QUADRATIC_COEFFICIENTS = dict(a=-0.4, b=4, c=-6.5)
X_START = 1.0
X_END = 10.0
NUM_POINTS = 200
ERROR_SCALE = 1.2


class PolyEstimator:
    """Simple polynomial fit model for sklearn.

    Credit: https://stackoverflow.com/a/52916579
    """

    def __init__(self, degree=2):
        self.degree = degree

    def fit(self, x, y):
        self.z = np.poly1d(np.polyfit(x.flatten().tolist(), y, self.degree))

    def predict(self, x):
        return self.z(x.flatten().tolist())


def parabola(
    x,
    a=QUADRATIC_COEFFICIENTS["a"],
    b=QUADRATIC_COEFFICIENTS["b"],
    c=QUADRATIC_COEFFICIENTS["c"],
):
    return a * (x ** 2) + (b * x) + c


x_values = np.sort(np.random.uniform(X_START, X_END, NUM_POINTS))
y_values = np.random.normal(list(map(parabola, x_values)), ERROR_SCALE)

# One input variable and len(x_values) observations
x_matrix = x_values[:, np.newaxis]

model = LinearRegression()
model.fit(x_matrix, y_values)
linear_fit_ys = model.predict(x_matrix)

poly = PolyEstimator(degree=2)
poly.fit(x_matrix, y_values)
poly_fit_ys = poly.predict(x_matrix)

df = pd.DataFrame(
    {
        "x": x_values,
        "y": y_values,
        "linear_fit": linear_fit_ys,
        "quadratic_fit": poly_fit_ys,
    }
)

df["linear_fit_error"] = (df.linear_fit - df.y).abs()
df["quadratic_fit_error"] = (df.quadratic_fit - df.y).abs()
df["linear_average_error"] = df.linear_fit_error.mean()
df["quadratic_average_error"] = df.quadratic_fit_error.mean()

ds = ColumnDataSource(df)
FIG_WIDTH = 400
RAW_DATA_ALPHA = 0.5
RAW_DATA_COLOR = "black"
VBAR_WIDTH = 0.01
LINEAR_COLOR = "green"
QUADRATIC_COLOR = "blue"
FIT_WIDTH = 10.0
FIT_ALPHA = 0.4
ERROR_HEIGHT = 250
MEAN_ERROR_ALPHA = 0.3
MEAN_ERROR_WIDTH = 5.0
MAIN_FIG_HEIGHT = 400
MAIN_FIG_KWARGS = dict(
    x_axis_label="some variable",
    height=MAIN_FIG_HEIGHT,
    width=FIG_WIDTH,
)
SCATTER_KWARGS = dict(
    x="x",
    y="y",
    source=ds,
    color=RAW_DATA_COLOR,
    alpha=RAW_DATA_ALPHA,
    legend_label="raw data",
)

main_raw_fig = figure(**MAIN_FIG_KWARGS, y_axis_label="some response")
main_raw_fig.scatter(**SCATTER_KWARGS)

main_linear_fig = figure(**MAIN_FIG_KWARGS, x_range=main_raw_fig.x_range)
main_linear_fig.scatter(**SCATTER_KWARGS)
main_linear_fig.line(
    x="x",
    y="linear_fit",
    source=ds,
    color=LINEAR_COLOR,
    width=FIT_WIDTH,
    alpha=FIT_ALPHA,
    legend_label="linear fit",
)

main_quadratic_fig = figure(**MAIN_FIG_KWARGS, x_range=main_raw_fig.x_range)
main_quadratic_fig.scatter(**SCATTER_KWARGS)
main_quadratic_fig.line(
    x="x",
    y="quadratic_fit",
    source=ds,
    color=QUADRATIC_COLOR,
    width=FIT_WIDTH,
    alpha=FIT_ALPHA,
    legend_label="quadratic fit",
)

line_error_fig = figure(
    height=ERROR_HEIGHT,
    width=FIG_WIDTH,
    x_range=main_raw_fig.x_range,
    y_axis_label="error",
)
line_error_fig.vbar(
    x="x",
    top="linear_fit_error",
    width=VBAR_WIDTH,
    source=ds,
    legend_label="linear fit residuals",
    color=LINEAR_COLOR,
)
line_error_fig.line(
    x="x",
    y="linear_average_error",
    color="red",
    alpha=MEAN_ERROR_ALPHA,
    width=MEAN_ERROR_WIDTH,
    line_dash="dashed",
    source=ds,
    legend_label="mean error",
)

quad_error_fig = figure(
    height=ERROR_HEIGHT,
    width=FIG_WIDTH,
    x_range=main_raw_fig.x_range,
    y_range=line_error_fig.y_range,
    y_axis_label="error",
)
quad_error_fig.vbar(
    x="x",
    top="quadratic_fit_error",
    width=VBAR_WIDTH,
    source=ds,
    color=QUADRATIC_COLOR,
    legend_label="quadratic fit residuals",
)
quad_error_fig.line(
    x="x",
    y="quadratic_average_error",
    color="red",
    line_dash="dashed",
    alpha=MEAN_ERROR_ALPHA,
    width=MEAN_ERROR_WIDTH,
    source=ds,
    legend_label="mean error",
)

combined = gridplot(
    [
        [main_raw_fig, main_linear_fig, main_quadratic_fig],
        [None, line_error_fig, quad_error_fig],
    ]
)

output_file("model_fitting.html")
show(combined)
