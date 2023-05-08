import webbrowser

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pearsonr

from cat_cont import cat_cont_correlation_ratio, cat_correlation
from htmlifier import htmlify
from hw_4_funcs import algos, diff_of_mean, eda_plots, rand_forest


def cont_subset(data, features, data_types):
    subset_df = []
    for feature in features:
        if data_types[feature] == "cont":
            subset_df.append((data[feature]))
    subset_df = pd.DataFrame(subset_df).T
    return subset_df


def cat_subset(data, features, data_types):
    subset_df = []
    for feature in features:
        if data_types[feature] == "cat":
            subset_df.append((data[feature]))
    subset_df = pd.DataFrame(subset_df).T
    return subset_df


def diff_mean_2d(data, feature_1, feature_2, response, data_types):
    means = []
    counts = []
    if (data_types[feature_1] == "cat" or len(data[feature_1].unique()) < 10) and (
        data_types[feature_2] == "cat" or len(data[feature_2].unique()) < 10
    ):
        feat1_sortbins = sorted(data[feature_1].unique())
        feat2_sortbins = sorted(data[feature_2].unique())
        for cat1 in feat1_sortbins:
            for cat2 in feat2_sortbins:
                bin_nums = data[response][
                    (data[feature_1] == cat1) & (data[feature_2] == cat2)
                ]
                means.append(np.nanmean(bin_nums))
                counts.append(len(bin_nums))
        hover_text = [str(count) if count > 0 else "" for count in counts]
        hover_text = np.array(hover_text).reshape(
            len(feat1_sortbins), len(feat2_sortbins)
        )
        # Calculating MoD
        means = np.array(means)
        weight = np.array(counts) / len(data)
        diff_unweighted = np.nansum(
            (means - np.nanmean(data[response])) ** 2
        ) / np.count_nonzero(~np.isnan(means))
        # that nan counting code is from kasimte.com/2020/02/13/how-do-i-count-numpy-nans.html
        diff_weighted = np.nansum((means - np.nanmean(data[response])) ** 2 * weight)
        means = means.reshape(len(feat1_sortbins), len(feat2_sortbins))
        fig = go.Figure(
            data=go.Heatmap(
                z=means, y=feat1_sortbins, x=feat2_sortbins, colorscale="RdBu"
            )
        )

    elif data_types[feature_1] == "cont" and (
        data_types[feature_2] == "cat" or len(data[feature_2].unique()) < 10
    ):
        # Establishing constants again
        feat1_min = data[feature_1].min()
        feat1_max = data[feature_1].max()
        step1 = (feat1_max - feat1_min) / 10
        feat2_sortbins = sorted(data[feature_2].unique())
        for i in range(0, 10):
            for cat in feat2_sortbins:
                bin_nums = data[response][
                    (data[feature_1] >= feat1_min + i * step1)
                    & (data[feature_1] <= feat1_min + (i + 1) * step1)
                    & (data[feature_2] == cat)
                ]
                means.append(np.nanmean(bin_nums))
                counts.append(len(bin_nums))
        weight = np.array(counts) / len(data)
        means = np.array(means)
        diff_unweighted = np.nansum(
            (means - np.nanmean(data[response])) ** 2
        ) / np.count_nonzero(~np.isnan(means))
        diff_weighted = np.nansum((means - np.nanmean(data[response])) ** 2 * weight)
        hover_text = [str(count) if count > 0 else "" for count in counts]
        hover_text = np.array(hover_text).reshape(10, len(feat2_sortbins))
        means = means.reshape(10, len(feat2_sortbins))
        # Making figure
        fig = go.Figure(
            data=go.Heatmap(
                z=means,
                y=np.arange(feat1_min, feat1_max, step1),
                x=feat2_sortbins,
                colorscale="RdBu",
            )
        )
    elif data_types[feature_2] == "cont" and (
        data_types[feature_1] == "cat" or len(data[feature_1].unique()) < 10
    ):
        # Establishing constants again
        feat2_min = data[feature_2].min()
        feat2_max = data[feature_2].max()
        step2 = (feat2_max - feat2_min) / 10
        feat1_sortbins = sorted(data[feature_1].unique())
        for i in range(0, 10):
            for cat in feat1_sortbins:
                bin_nums = data[response][
                    (data[feature_2] >= feat2_min + i * step2)
                    & (data[feature_2] <= feat2_min + (i + 1) * step2)
                    & (data[feature_1] == cat)
                ]
                means.append(np.nanmean(bin_nums))
                counts.append(len(bin_nums))
        weight = np.array(counts) / len(data)
        means = np.array(means)
        diff_unweighted = np.nansum(
            (means - np.nanmean(data[response])) ** 2
        ) / np.count_nonzero(~np.isnan(means))
        diff_weighted = np.nansum((means - np.nanmean(data[response])) ** 2 * weight)
        hover_text = [str(count) if count > 0 else "" for count in counts]
        hover_text = np.array(hover_text).reshape(10, len(feat1_sortbins))
        means = means.reshape(10, len(feat1_sortbins))
        # Making figure
        fig = go.Figure(
            data=go.Heatmap(
                z=means,
                y=np.arange(feat2_min, feat2_max, step2),
                x=feat1_sortbins,
                colorscale="RdBu",
            )
        )
    elif data_types[feature_1] == "cont" and data_types[feature_2] == "cont":
        # Establishing some constants
        feat1_min = data[feature_1].min()
        feat1_max = data[feature_1].max()
        step1 = (feat1_max - feat1_min) / 10
        feat2_max = data[feature_2].max()
        feat2_min = data[feature_2].min()
        step2 = (feat2_max - feat2_min) / 10
        # Nested For Loop computations

        for i in range(0, 10):
            for j in range(0, 10):
                bin_num = data[response][
                    (data[feature_1] >= feat1_min + i * step1)
                    & (data[feature_1] <= feat1_min + (i + 1) * step1)
                    & (data[feature_2] >= feat2_min + j * step2)
                    & (data[feature_2] <= feat2_min + (j + 1) * step2)
                ]
                means.append(np.nanmean(bin_num))
                counts.append(len(bin_num))
        means = np.array(means)
        counts = np.array(counts)
        # Calculating MoDs
        weight = np.array(counts) / len(data)
        diff_unweighted = np.nansum(
            (means - np.nanmean(data[response])) ** 2
        ) / np.count_nonzero(~np.isnan(means))
        diff_weighted = np.nansum((means - np.nanmean(data[response])) ** 2 * weight)
        hover_text = [str(count) if count > 0 else "" for count in counts]
        hover_text = np.array(hover_text).reshape(10, 10)
        means = means.reshape(10, 10)
        # Making figure
        fig = go.Figure(
            data=go.Heatmap(
                z=means,
                y=np.arange(feat1_min, feat1_max, step1),
                x=np.arange(feat2_min, feat2_max, step2),
                colorscale="RdBu",
            )
        )
    fig.update_traces(text=hover_text, texttemplate="%{text}")

    fig.update_layout(title=f"{feature_1} vs {feature_2} MoR Plot")

    fig.update_yaxes(title=f"{feature_1}")
    fig.update_xaxes(title=f"{feature_2}")
    fig.write_html(
        f"figures/{feature_1} vs {feature_2} MoR Plot.html", include_plotlyjs="cdn"
    )

    return diff_unweighted, diff_weighted


def midterm_stuff(ds_name, data, features, response):

    data = data.dropna()
    # Determining data_types
    data_types = {}
    if len(data[response].unique()) == 2:
        data_types[response] = "bool"
    else:
        data_types[response] = "cont"
    for feature in features:
        if isinstance(data[feature][0], str) or (len(data[feature].unique()) == 2):
            data_types[feature] = "cat"
        else:
            data_types[feature] = "cont"
    print(data_types)
    # Same df from hw_04
    df = pd.DataFrame(
        columns=[
            "Response",
            "Predictor",
            "Response Type",
            "Predictor Type",
            "EDA",
            "P Value",
            "T Statistic",
            "MoR Plot",
            "Diff of Mean (unweighted)",
            "Diff of Mean (weighted)",
        ]
    )
    # Making the original hw_04 table
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
            f"figures/{feature} vs {response} MoR plot.html",
            unw,
            w,
        ]

    col = rand_forest(data, response, features, data_types)
    df["Random Forest"] = col
    # From StackOverflow hints
    df = htmlify(df, link_cols=["EDA", "MoR Plot"])
    # df.to_html(f"{ds_name} df.html", render_links=True, escape=False)

    # webbrowser.open(f"{ds_name} df.html")
    # Repeating but with cont-cont pearson
    df_pearson = pd.DataFrame(
        columns=["cont_1", "cont_2", "pearson corr", "cont_1 plot", "cont_2 plot"]
    )
    df_bf_contcont = pd.DataFrame(
        columns=[
            "cont_1",
            "cont_2",
            "diff of mean (uw)",
            "diff of mean (w)",
            "MoR Plot",
        ]
    )
    subset_cont = cont_subset(data, features, data_types)
    cont_features = subset_cont.columns
    for idx1, feature_1 in enumerate(cont_features):
        for idx2, feature_2 in enumerate(cont_features):
            if idx2 > idx1:
                corr, _ = pearsonr(data[feature_1], data[feature_2])
                df_pearson.loc[len(df_pearson)] = [
                    feature_1,
                    feature_2,
                    corr,
                    f"figures/{feature_1} vs {response} EDA plot.html",
                    f"figures/{feature_2} vs {response} EDA plot.html",
                ]
                uw, w = diff_mean_2d(data, feature_1, feature_2, response, data_types)
                df_bf_contcont.loc[len(df_bf_contcont)] = [
                    feature_1,
                    feature_2,
                    uw,
                    w,
                    f"figures/{feature_1} vs {feature_2} MoR Plot.html",
                ]
    df_pearson = htmlify(
        df_pearson, link_cols=["cont_1 plot", "cont_2 plot"], sort_col="pearson corr"
    )
    df_pearson.to_html("Pearson.html", render_links=True, escape=False)
    df_bf_contcont = htmlify(
        df_bf_contcont, link_cols=["MoR Plot"], sort_col="diff of mean (w)"
    )
    df_bf_contcont.to_html(
        "Cont Cont Brute Force.html", render_links=True, escape=False
    )
    # Correlation Plot Pearson
    df_pcorr = subset_cont.corr()
    fig = px.imshow(
        df_pcorr, zmin=-1, zmax=1, text_auto=True, color_continuous_scale="Edge_r"
    )
    fig.write_html("figures/Pearson Matrix.html", include_plotlyjs="cdn")

    # Repeat but for cat-cat
    df_cramer = pd.DataFrame(
        columns=["cat_1", "cat_2", "Cramer corr", "cat_1 plot", "cat_2 plot"]
    )
    df_tschuprow = pd.DataFrame(
        columns=["cat_1", "cat_2", "Tschuprow corr", "cat_1 plot", "cat_2 plot"]
    )
    df_bf_catcat = pd.DataFrame(
        columns=["cat_1", "cat_2", "diff of mean (uw)", "diff of mean (w)", "MoR Plot"]
    )
    subset_cat = cat_subset(data, features, data_types)
    cat_features = subset_cat.columns
    c_matrix = np.ones((len(cat_features), len(cat_features)))
    t_matrix = np.ones((len(cat_features), len(cat_features)))
    for idx1, feature_1 in enumerate(cat_features):
        for idx2, feature_2 in enumerate(cat_features):
            if idx2 > idx1:
                c_corr = cat_correlation(data[feature_1], data[feature_2])
                t_corr = cat_correlation(
                    data[feature_1], data[feature_2], tschuprow=True
                )
                c_matrix[idx1, idx2] = c_corr
                c_matrix[idx2, idx1] = c_corr
                t_matrix[idx1, idx2] = t_corr
                t_matrix[idx2, idx1] = t_corr
                df_cramer.loc[len(df_cramer)] = [
                    feature_1,
                    feature_2,
                    c_corr,
                    f"figures/{feature_1} vs {response} EDA plot.html",
                    f"figures/{feature_2} vs {response} EDA plot.html",
                ]
                df_tschuprow.loc[len(df_tschuprow)] = [
                    feature_1,
                    feature_2,
                    t_corr,
                    f"figures/{feature_1} vs {response} EDA plot.html",
                    f"figures/{feature_2} vs {response} EDA plot.html",
                ]
                uw, w = diff_mean_2d(data, feature_1, feature_2, response, data_types)
                df_bf_catcat.loc[len(df_bf_catcat)] = [
                    feature_1,
                    feature_2,
                    uw,
                    w,
                    f"figures/{feature_1} vs {feature_2} MoR Plot.html",
                ]
    df_cramer = htmlify(
        df_cramer, link_cols=["cat_1 plot", "cat_2 plot"], sort_col="Cramer corr"
    )
    df_cramer.to_html("Cramer.html", render_links=True, escape=False)
    df_tschuprow = htmlify(
        df_tschuprow, link_cols=["cat_1 plot", "cat_2 plot"], sort_col="Tschuprow corr"
    )
    df_tschuprow.to_html("Tschuprow.html", render_links=True, escape=False)
    df_bf_catcat = htmlify(
        df_bf_catcat, link_cols=["MoR Plot"], sort_col="diff of mean (w)"
    )
    df_bf_catcat.to_html("Cat Cat Brute Force.html", render_links=True, escape=False)

    fig = px.imshow(
        c_matrix,
        x=cat_features,
        y=cat_features,
        zmin=-1,
        zmax=1,
        text_auto=True,
        color_continuous_scale="Edge_r",
    )
    fig.write_html("figures/Cramer's Matrix.html", include_plotlyjs="cdn")
    fig = px.imshow(
        t_matrix,
        x=cat_features,
        y=cat_features,
        zmin=-1,
        zmax=1,
        text_auto=True,
        color_continuous_scale="Edge_r",
    )
    fig.write_html("figures/Tschuprow's Matrix.html", include_plotlyjs="cdn")
    # Continuous Categorical
    df_cc = pd.DataFrame(
        columns=["cont_feature", "cat_feature", "corr ratio", "cont EDA", "cat EDA"]
    )
    df_bf_cc = pd.DataFrame(
        columns=[
            "cont_feature",
            "cat_feature",
            "diff of mean (uw)",
            "diff of mean (w)",
            "MoR Plot",
        ]
    )
    catcont_matrix = np.zeros((len(cont_features), len(cat_features)))
    for idx1, feature_1 in enumerate(cont_features):
        for idx2, feature_2 in enumerate(cat_features):
            cn_ratio = cat_cont_correlation_ratio(
                categories=data[feature_2], values=data[feature_1]
            )
            catcont_matrix[idx1, idx2] = cn_ratio
            df_cc.loc[len(df_cc)] = [
                feature_1,
                feature_2,
                cn_ratio,
                f"figures/{feature_1} vs {response} EDA plot.html",
                f"figures/{feature_2} vs {response} EDA plot.html",
            ]
            uw, w = diff_mean_2d(data, feature_1, feature_2, response, data_types)
            df_bf_cc.loc[len(df_bf_cc)] = [
                feature_1,
                feature_2,
                uw,
                w,
                f"figures/{feature_1} vs {feature_2} MoR Plot.html",
            ]

    df_bf_cc = htmlify(df_bf_cc, link_cols=["MoR Plot"], sort_col="diff of mean (w)")
    df_bf_cc.to_html("Cont Cat Brute Force.html", render_links=True, escape=False)
    df_cc = htmlify(df_cc, link_cols=["cont EDA", "cat EDA"], sort_col="corr ratio")
    df_cc.to_html("ContCat.html", render_links=True, escape=False)
    fig = px.imshow(
        catcont_matrix,
        y=cont_features,
        x=cat_features,
        zmin=-1,
        zmax=1,
        text_auto=True,
        color_continuous_scale="Edge_r",
    )
    cc_fig = fig.write_html("figures/CatCont Matrix.html", include_plotlyjs="cdn")
    print(cc_fig)
    # Reading Figures as HTMLs
    with open("figures/Tschuprow's Matrix.html", "r") as f:
        Tschuprow = f.read()
    with open("figures/Cramer's Matrix.html", "r") as g:
        Cramer = g.read()
    with open("figures/CatCont Matrix.html", "r") as h:
        CatCont = h.read()
    with open("figures/Pearson Matrix.html", "r") as i:
        Pearson = i.read()
    # Combining everything into final HTML doc

    with open("Feature Analysis.html", "w") as midterm:
        midterm.write(
            f"<h1> {ds_name} </h1>"
            + df.to_html(render_links=True, escape=False, index=False)
            + "<h1> Categorical/Categorical Predictor </h1>"
            + "<h2> Tschuprow </h2>"
            + Tschuprow
            + df_tschuprow.to_html(render_links=True, escape=False, index=False)
            + "<h2> Cramer </h2>"
            + Cramer
            + df_cramer.to_html(render_links=True, escape=False, index=False)
            + "<h2> Categorical/Continuous Predictors</h2>"
            + CatCont
            + df_cc.to_html(render_links=True, escape=False, index=False)
            + "<h2> Continuous/Continuous Predictors </h2>"
            + Pearson
            + df_pearson.to_html(render_links=True, escape=False, index=False)
            + "<h1> Brute Force </h1>"
            + "<h2> Categorical/Categorical </h2>"
            + df_bf_catcat.to_html(render_links=True, escape=False, index=False)
            + "<h2> Categorical/Continuous </h2>"
            + df_bf_cc.to_html(render_links=True, escape=False, index=False)
            + "<h2> Continuous/Continuous </h2>"
            + df_bf_contcont.to_html(render_links=True, escape=False, index=False)
        )

    webbrowser.open("Feature Analysis.html")

    return
