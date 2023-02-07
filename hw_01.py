import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def print_heading(
    title,
):  # This was in your code Julien so I kept it here to make things pretty
    print("*" * 80)
    print(title)
    print("*" * 80)
    return


def summary(iris, feat):  # just a function so I don't have to type print over and over
    print(feat + " Min: ", np.min(iris[feat]))
    print(feat + " 25%: ", np.quantile(iris[feat], 0.25))
    print(feat + " Median: ", np.quantile(iris[feat], 0.5))
    print(feat + " 75%: ", np.quantile(iris[feat], 0.75))
    print(feat + " Max: ", np.max(iris[feat]))
    print(feat + " Mean: ", np.mean(iris[feat]))
    return


def diff_of_mean(iris, species, variable):
    fig = make_subplots(specs=[[{"secondary_y": True}]])  # This was taken from:
    dummies = pd.get_dummies(iris["species"])
    data = iris[variable]
    maxi = np.max(data)
    mini = np.min(data)
    step = (maxi - mini) / 5
    fig.add_trace(
        go.Histogram(x=data, xbins=dict(start=mini, end=maxi, size=step), name="count")
    )
    fig.add_trace(
        go.Scatter(
            x=data, y=np.ones(len(data)) * np.mean(dummies[species]), name=r"$\mu_0$"
        ),
        secondary_y=True,
    )  # horizontal line
    # computing proportion in each bin
    means = []
    mid_bin = []
    for i in range(0, 5):
        count = dummies[species][
            (data > mini + i * step) & (data < mini + (i + 1) * step)
        ]
        means.append(np.mean(count))
        mid_bin.append(mini + (2 * i + 1) / 2 * step)

    fig.add_trace(go.Scatter(x=mid_bin, y=means, name=r"$\mu_i$"), secondary_y=True)

    # Add figure title
    fig.update_layout(title_text="{} {} Difference of Means".format(species, variable))

    # Set x-axis title
    fig.update_xaxes(title_text="{}".format(variable))

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Count</b>", secondary_y=False)
    fig.update_yaxes(
        title_text="<b>Likelihood of Being {}</b> ".format(species), secondary_y=True
    )

    fig.write_html(
        species + " " + variable + " difference of means.html", include_plotlyjs="cdn"
    )
    fig.show()
    return


def main():
    # Increase pandas print viewport (so we see more on the screen)
    pd.set_option("display.max_rows", 10)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1_000)

    # Load the famous iris data set

    iris = px.data.iris()
    print(iris)
    # A lot of this code is just the same as the Titanic code but replaced the preprocessing type and dataset.
    # Very similar to your slides

    print_heading("Selecting Features")
    print(iris[["sepal_length", "sepal_width", "petal_length", "petal_width"]])

    # DataFrame to numpy values
    X_orig = iris[["sepal_length", "sepal_width", "petal_length", "petal_width"]].values
    y = iris["species"].values

    # Printing out some basic statistics.
    summary(iris, "sepal_length")
    summary(iris, "sepal_width")
    summary(iris, "petal_length")
    summary(iris, "petal_width")

    # 5 Basic Plots and Saving them
    # These types of plots can be seen on Plotly's website under Distribution Plots.
    fig1 = px.box(
        iris, x=iris["species"], color=iris["species"], y=iris["sepal_length"]
    )
    fig1.write_html("Iris Box Plot.html", include_plotlyjs="cdn")
    fig2 = px.violin(
        iris, x=iris["species"], color=iris["species"], y=iris["petal_length"]
    )
    fig2.write_html("Iris Violin Plot.html", include_plotlyjs="cdn")
    fig3 = px.histogram(
        iris,
        x="sepal_length",
        y="petal_length",
        color="species",
        marginal="box",
        hover_data=iris.columns,
    )
    fig3.write_html("Iris Sepal Length vs Petal Length.html", include_plotlyjs="cdn")
    fig4 = px.scatter(iris, x="sepal_width", y="petal_width", color="species")
    fig4.write_html("Iris Sepal Width vs Petal Width.html", include_plotlyjs="cdn")
    fig5 = px.density_heatmap(
        iris, x="sepal_length", y="sepal_width", marginal_x="box", marginal_y="box"
    )
    fig5.write_html("Iris Sepal Length vs Sepal Width.html", include_plotlyjs="cdn")

    fig1.show()
    fig2.show()
    fig3.show()
    fig4.show()
    fig5.show()
    # Let's generate a feature from the where they started
    stand_scale = StandardScaler()
    stand_scale.fit(X_orig)
    X = stand_scale.transform(X_orig)

    # Fit the features to a random forest
    random_forest = RandomForestClassifier(random_state=1234)
    random_forest.fit(X, y)

    test_df = pd.DataFrame.from_dict(
        # I just made up some random numbers with enough range to hopefully hit all the flower types
        [
            {
                "sepal_length": 3.4,
                "sepal_width": 1.2,
                "petal_length": 4.2,
                "petal_width": 1.1,
            },
            {
                "sepal_length": 2.6,
                "sepal_width": 1.6,
                "petal_length": 1.4,
                "petal_width": 1.5,
            },
            {
                "sepal_length": 1.4,
                "sepal_width": 0.6,
                "petal_length": 3.7,
                "petal_width": 0.8,
            },
            {
                "sepal_length": 3.1,
                "sepal_width": 0.9,
                "petal_length": 2.8,
                "petal_width": 2.7,
            },
        ]
    )
    print_heading("Dummy data to predict")
    print(test_df)

    X_test_orig = test_df.values
    X_test = stand_scale.transform(X_test_orig)
    prediction = random_forest.predict(X_test)
    probability = random_forest.predict_proba(X_test)

    print_heading("Model Predictions")
    print(f"Classes: {random_forest.classes_}")
    print(f"Probability: {probability}")
    print(f"Predictions: {prediction}")

    # As pipeline
    print_heading("Model via Pipeline Predictions")
    pipeline = Pipeline(
        [
            ("StandardScaler", StandardScaler()),
            ("RandomForest", RandomForestClassifier(random_state=1234)),
        ]
    )
    pipeline.fit(X_orig, y)

    probability = pipeline.predict_proba(X_test_orig)
    prediction = pipeline.predict(X_test_orig)
    print(f"Probability: {probability}")
    print(f"Predictions: {prediction}")

    # Mean of Difference Plots
    for species in iris["species"].unique():
        # Yes I know nested for loops are bad practice
        # But this is what I came up with
        for variable in iris.columns[:-2]:
            # Ignoring last 2 columns b/c that is species and speciesid
            diff_of_mean(iris, species, variable)
    return


if __name__ == "__main__":
    sys.exit(main())
