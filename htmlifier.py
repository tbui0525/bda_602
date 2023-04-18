import pandas as pd
from pretty_html_table import build_table


def htmlify(dataframe, link_cols, sort_col=None):
    for i in link_cols:
        dataframe[i] = dataframe[i].apply(
            lambda x: "<a href='{}'target='_blank'>{}</a>".format(x, "Plot")
        )
        if sort_col:
            dataframe = dataframe.sort_values(
                by=[sort_col], ascending=False, key=pd.Series.abs
            )
    return dataframe


def colorize(val):
    if val > 0:
        color = "blue"
    elif val < 0:
        color = "red"
    else:
        color = "black"
    return "color: %s" % color


def aesthetic(dataframe):
    # dataframe = dataframe.style.applymap(colorize)
    dataframe = build_table(dataframe, "grey_dark")

    return dataframe
