import sys

import numpy as np
import plotly.express as px
import statsmodels.api as sm

from dataset_loader import TestDatasets


def algos(data, feature, response, data_types):
    y = data[response]
    x = data[feature]
    if data_types[response] == "cont" and data_types[feature] == "cont":
        predictor = sm.add_constant(x)
        linreg = sm.OLS(y, predictor).fit()
        print(f"Variable: {feature}")
        print(linreg.summary())

        t_value = round(linreg.tvalues[1], 6)
        p_value = "{:.6e}".format(linreg.pvalues[1])
        print("t_val: ", t_value)
        print("p_val: ", p_value)
        fig = px.scatter(x=x, y=y, trendline="ols")
        fig.show()
    elif data_types[response] == "bool" and data_types[feature] == "cont":
        x = sm.add_constant(x)
        linreg = sm.Logit(y, x).fit()
        print(f"Variable: {feature}")
        print(linreg.summary())

        t_value = round(linreg.tvalues[1], 6)
        p_value = "{:.6e}".format(linreg.pvalues[1])
        print("t_val: ", t_value)
        print("p_val: ", p_value)
        fig = px.scatter(x=x, y=y, trendline="")

        fig.show()
    return


def eda_plots(data, feature, response, data_types):
    if data_types[response] == "bool":
        if data_types[feature] == "cat":
            cats = data[feature].unique()
            z = np.zeros((len(cats), 2))
            feated = data.groupby([feature]).mean()
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
    fig.show()

    return


def main():
    td = TestDatasets()
    data, features, response = td.get_test_data_set(data_set_name="mpg")
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

    for feature in features:
        #    eda_plots(data, feature, response, data_types)
        #    print(feature)
        algos(data, feature, response, data_types)

    return 0


if __name__ == "__main__":
    sys.exit(main())
