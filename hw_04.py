import os.path
import sys
import webbrowser

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier

from dataset_loader import TestDatasets


def rand_forest(data, response, features, data_types):
    forest = RandomForestClassifier(n_estimators=100, random_state=1234)
    col = []
    subset_df = []
    for feature in features:
        if data_types[feature] == "cont":
            subset_df.append((data[feature]))
    subset_df = pd.DataFrame(subset_df).T
    forest.fit(subset_df, data[response])
    rank_vals = forest.feature_importances_
    feat_dict = {}
    for idx, feature in enumerate(subset_df.columns):
        feat_dict[feature] = rank_vals[idx]
    for feature in features:
        if data_types[feature] == "cont":
            col.append(feat_dict[feature])
        else:
            col.append(None)

    return col


def diff_of_mean(data, feature, response, data_types):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if data_types[feature] == "cat":
        bin_num = len(data[feature].unique())
        fig.add_trace(go.Histogram(x=data[feature]))
        fig.add_trace(
            go.Scatter(
                x=data[feature],
                y=np.ones(len(data[feature].unique())) * np.mean(data[response]),
            ),
            secondary_y=True,
        )
        means = data.groupby([feature])[response].mean()
        fig.add_trace(go.Scatter(x=means.index, y=means), secondary_y=True)
        weight = []
        for cat in means.index:
            weight.append(sum(data[feature] == cat) / len(data))
        diff_unweighted = sum((means - data[response].mean()) ** 2)
        diff_weighted = sum((means - data[response].mean()) ** 2 * weight)
    else:
        maxi = data[feature].max()
        mini = data[feature].min()
        step = (maxi - mini) / 10
        fig.add_trace(
            go.Histogram(
                x=data[feature],
                xbins=dict(start=mini, end=maxi, size=step),
                name="count",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data[feature],
                y=np.ones(len(data[feature].unique())) * np.mean(data[response]),
                name=r"$\mu_0$",
            ),
            secondary_y=True,
        )  # horizontal line
        # computing proportion in each bin
        means = []
        mid_bin = []
        count = []
        for i in range(0, 10):
            bin_num = data[response][
                (data[feature] >= mini + i * step)
                & (data[feature] <= mini + (i + 1) * step)
            ]
            means.append(np.mean(bin_num))
            count.append(len(bin_num))
            mid_bin.append(mini + (2 * i + 1) / 2 * step)

        fig.add_trace(go.Scatter(x=mid_bin, y=means, name=r"$\mu_i$"), secondary_y=True)
        means = np.array(means)
        weight = np.array(count) / len(data)
        diff_unweighted = np.nansum((means - np.mean(data[response])) ** 2) / 10
        diff_weighted = np.nansum((means - np.mean(data[response])) ** 2 * weight) / 10
    fig.write_html(
        f"figures/{feature} vs {response} MoD plot.html", include_plotlyjs="cdn"
    )
    return diff_unweighted, diff_weighted


def make_clickable(val):
    f_url = os.path.basename(val)
    return '<a href="{}">{}</a>'.format(val, f_url)


def algos(data, feature, response, data_types):
    y = data[response]
    x = data[feature]
    if data_types[response] == "cont" and data_types[feature] == "cont":
        predictor = sm.add_constant(x)
        linreg = sm.OLS(y, predictor).fit()

        t_value = round(linreg.tvalues[1], 6)
        p_value = "{:.6e}".format(linreg.pvalues[1])
        print("t_val: ", t_value)
        print("p_val: ", p_value)
        # fig = px.scatter(x=x, y=y, trendline="ols")

    elif data_types[response] == "bool" and data_types[feature] == "cont":
        x = sm.add_constant(x)
        linreg = sm.Logit(y, x).fit()

        t_value = round(linreg.tvalues[1], 6)
        p_value = "{:.6e}".format(linreg.pvalues[1])
        print("t_val: ", t_value)
        print("p_val: ", p_value)

        # fig.show()
    else:
        t_value = None
        p_value = None
    return t_value, p_value


def eda_plots(data, feature, response, data_types):
    if data_types[response] == "bool":
        if data_types[feature] == "cat":
            cats = data[feature].unique()
            z = np.zeros((len(cats), 2))
            feated = data.groupby([feature]).mean(numeric_only=True)
            z[:, 0] = feated[response]
            z[:, 1] = 1 - feated[response]
            fig = px.imshow(z, x=["True", "False"], y=feated.index, text_auto=True)

        else:
            fig = px.violin(data, x=response, color=response, y=feature)

    else:
        if data_types[feature] == "cat":
            fig = px.violin(data, x=feature, y=response, color=feature)

        else:
            fig = px.scatter(data, feature, response, trendline="ols")
    # fig.show()
    fig.write_html(
        f"figures/{feature} vs {response} EDA plot.html", include_plotlyjs="cdn"
    )
    return


def main():
    td = TestDatasets()
    ds_name = "titanic"
    data, features, response = td.get_test_data_set(data_set_name=ds_name)
    data = data.dropna()
    data_types = {}
    if len(data[response].unique()) == 2:
        data_types[response] = "bool"
    else:
        data_types[response] = "cont"
    for feature in features:
        if isinstance(data[feature][0], str) or len(data[feature].unique()) == 2:
            data_types[feature] = "cat"
        else:
            data_types[feature] = "cont"
    print(data_types)
    df = pd.DataFrame(
        columns=[
            "Response",
            "Predictor",
            "Response Type",
            "Predictor Type",
            "EDA",
            "P Value",
            "T Statistic",
            "MoD Plot",
            "Diff of Mean (unweighted)",
            "Diff of Mean (weighted)",
        ]
    )

    for feature in features:
        eda_plots(data, feature, response, data_types)
        print(feature)
        t, p = algos(data, feature, response, data_types)
        unw, w = diff_of_mean(data, feature, response, data_types)
        df.loc[len(df)] = [
            response,
            feature,
            data_types[response],
            data_types[feature],
            f"figures/{feature} vs {response} EDA plot.html",
            p,
            t,
            f"figures/{feature} vs {response} MoD plot.html",
            unw,
            w,
        ]

    col = rand_forest(data, response, features, data_types)
    df["Random Forest"] = col
    df.style.format({"EDA": make_clickable})
    df.to_html(f"{ds_name} df.html")

    webbrowser.open(f"{ds_name} df.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
