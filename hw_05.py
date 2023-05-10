import sys

import numpy as np
import pandas as pd
import sqlalchemy
import statsmodels.api
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import scale
from sqlalchemy import text
from statsmodels.api import Logit

from midterm import midterm_stuff


def dead_trees(
    x_train, y_train, x_test, y_test, hinge=0
):  # get it? Cuz logs are dead trees?
    if hinge == 0:
        predictor = statsmodels.api.add_constant(x_train)
        pred_test = statsmodels.api.add_constant(x_test)
    else:
        predictor = x_train
        pred_test = x_test
    pcr_log_model = Logit(y_train, predictor)
    pcr_log_model_fitted = pcr_log_model.fit()
    print(pcr_log_model_fitted.summary())
    pcr_log_pred = pcr_log_model_fitted.predict(pred_test)
    log_roc_auc = roc_auc_score(y_test, pcr_log_pred)
    # Using AUC to evaluate model instead of just accuracy or precision.
    print("Logistic ROC AUC Score: ", log_roc_auc)


def trees(
    x_train, y_train, x_test, y_test
):  # get it? Cuz forests are a bunch of trees?
    forest = RandomForestClassifier(n_estimators=100, random_state=69, max_depth=7)
    forest.fit(x_train, y_train)
    y_rf_pred = forest.predict(x_test)
    rf_roc_auc = roc_auc_score(y_test, y_rf_pred)

    print("Random Forest ROC AUC Score: ", rf_roc_auc)


def model(data, features, hinge=0):
    split_point = int(len(data) * 0.8)  # creates split point for train-test
    print(split_point)
    train_data = data[:split_point]  # everything up to split point
    y_train = train_data["Home_Team_Win"]
    x_train = train_data[features]
    test_data = data[split_point:]  # everything from split point
    y_test = test_data["Home_Team_Win"]
    x_test = test_data[features]

    # Logistic Reg
    dead_trees(x_train, y_train, x_test, y_test, hinge)

    # Using AUC to evaluate model instead of just accuracy or precision.

    trees(x_train, y_train, x_test, y_test)


def main():
    user = "root"
    password = "jIg688xaj?"  # pragma: allowlist secret
    # host = "localhost"
    host = "mariadb_container"
    db = "baseball"
    connect_string = f"mariadb+mariadbconnector://{user}:{password}@{host}/{db}"  # pragma: allowlist secret
    sql_engine = sqlalchemy.create_engine(connect_string)

    query = """
    SELECT * FROM final_table
    """
    data = pd.DataFrame(sql_engine.connect().execute(text(query)))
    response = "Home_Team_Win"
    features = list(data.columns[4:-1])

    data = data.reset_index()

    print(features)
    print(data[response])
    for feature in features:
        data[feature] = data[feature].astype(float)
        data[feature] = data[feature].fillna(np.nanmean(data[feature]))
    data[response] = data[response].astype(bool)

    midterm_stuff("Baseball", data, features, response, name="")
    """
    Looking at those charts, there is clearly an outlier bias going on that may impact the model, so
    I will clip the outlier data before continuing analysis
    """

    for feature in features:
        low, high = data[feature].quantile([0.05, 0.95])
        data[feature] = data[feature].clip(low, high)

    midterm_stuff("Baseball", data, features, response, "Clipped ")
    """
    Based on this Feature Analysis HTML, we see our two strongest independent features OBP and inn_p also
    have the 2nd highest Brute Force MoR value. Let's add that feature into our dataset. Since it is in pandas, we
    can simply add the column
    """
    # data["OBP_inn_p"] = (data["diff_OBP"]+1)/(data["diff_inn_p"]+1)
    # features = list(data.columns[4:].drop("Home_Team_Win"))
    # For train-test split, we cannot do a random split because the data is time-based.
    # The data is already sorted by local_date, so we can split it 80-20 directly
    model(data, features)

    """
    ROC AUC socre is 52.5 for Logistic and 50 for Random Forest. Let's drop some not so good features.
    Looks like CERA has and PTB are really bad. Anything with P > 0.05 will be dropped
    """

    pca = PCA()
    pca.fit_transform(scale(data[features]))
    print(np.cumsum(np.round(pca.explained_variance_ratio_, decimals=4) * 100))

    split_point = int(len(data) * 0.8)  # creates split point for train-test
    print(split_point)
    train_data = data[:split_point]  # everything up to split point
    y_train = train_data["Home_Team_Win"]
    x_train = train_data[features]
    test_data = data[split_point:]  # everything from split point
    y_test = test_data["Home_Team_Win"]
    x_test = test_data[features]

    pca_train = pca.fit_transform(scale(x_train))[:, 0:7]
    pca_test = pca.transform(scale(x_test))[:, 0:7]

    dead_trees(pca_train, y_train, pca_test, y_test)
    trees(pca_train, y_train, pca_test, y_test)
    """
    53.7 for PCA Logit and 49.8 for PCA Random Forest. So significantly better than no PCA
    """
    # Looks like first 7 features cover about 95% of variance. First 6 covers about 90%. Unsure which to choose
    new_data = data.drop(
        [
            "diff_BA",
            "diff_Score_Diff",
            "diff_thrown",
            "diff_ppi",
            "diff_CERA",
            "diff_PTB",
        ],
        axis=1,
    )
    reduced_features = new_data.columns[4:].drop("Home_Team_Win")
    model(new_data, reduced_features)
    pca_train = pca_train[:, [1, 3, 4, 6]]
    pca_test = pca_test[:, [1, 3, 4, 6]]
    dead_trees(pca_train, y_train, pca_test, y_test)
    trees(pca_train, y_train, pca_test, y_test)
    #
    # Logit did not change much, but we reduced features, so that is good nonetheless, Random Forest had minor
    # improvements, but the key improvements were made in the PCA computations with PCA Logit (without sprinkles)
    # breaking the 54 barrier and Random Forest finally being slightly better than guessing. Let's see what happens
    # when we take our best features and a knot point where the slope changes.
    # """
    newer_data = new_data.drop("diff_Pythag", axis=1)
    newer_data["OBP_hinge"] = [max(0, i - 0.01) for i in data["diff_OBP"].tolist()]

    reducer_features = newer_data.columns[4:].drop(["Home_Team_Win"])
    model(newer_data, reducer_features, hinge=1)

    pca.fit_transform(scale(newer_data[reducer_features]))
    print(np.cumsum(np.round(pca.explained_variance_ratio_, decimals=4) * 100))
    split_point = int(len(newer_data) * 0.8)  # creates split point for train-test
    print(split_point)
    train_data = newer_data[:split_point]  # everything up to split point
    y_train = train_data["Home_Team_Win"]
    x_train = train_data[reducer_features]
    test_data = newer_data[split_point:]  # everything from split point
    y_test = test_data["Home_Team_Win"]
    x_test = test_data[reducer_features]

    pca_train = pca.fit_transform(scale(x_train))[:, 0:6]
    pca_test = pca.transform(scale(x_test))[:, 0:6]

    dead_trees(pca_train, y_train, pca_test, y_test)
    trees(pca_train, y_train, pca_test, y_test)

    """
        After adding hinge points we now have OG Logit at 54.2, Rand Forest at 49.4 (Poor random forest)
        PCA Logit at about 55 (new barrier broken!) and random forest at 49.9. I think that although I could do
        more for the final project, this is a good place to end.
    """

    return 0


if __name__ == "__main__":
    sys.exit(main())
