import sys

from sklearn.ensemble import RandomForestClassifier
import statsmodels.api
from statsmodels.api import Logit
from sklearn.metrics import classification_report, roc_auc_score
import pandas as pd
import sqlalchemy
from sqlalchemy import text

from midterm import midterm_stuff


def model(data, features):
    split_point = int(len(data) * 0.8)  # creates split point for train-test
    print(split_point)
    train_data = data[:split_point]  # everything up to split point
    y_train = train_data["Home_Team_Win"]
    x_train = train_data[features]
    test_data = data[split_point:]  # everything from split point
    y_test = test_data["Home_Team_Win"]
    x_test = test_data[features]
    predictor = statsmodels.api.add_constant(x_train)
    pred_test = statsmodels.api.add_constant(x_test)
    logreg_model = Logit(y_train, predictor)
    logreg_model_fitted = logreg_model.fit()
    print(logreg_model_fitted.summary())

    y_log_pred = logreg_model_fitted.predict(pred_test)
    log_roc_auc = roc_auc_score(y_test, y_log_pred)

    # Using AUC to evaluate model instead of just accuracy or precision.
    print("Logistic ROC AUC Score: ", log_roc_auc)

    forest = RandomForestClassifier(n_estimators=100, random_state=69)
    forest.fit(x_train, y_train)
    y_rf_pred = forest.predict(x_test)
    rf_roc_auc = roc_auc_score(y_test, y_rf_pred)

    print("Random Forest ROC AUC Score: ", rf_roc_auc)


def main():
    user = "root"
    password = "jIg688xaj?"  # pragma: allowlist secret
    host = "localhost"
    #host = "mariadb_container"
    db = "baseball"
    connect_string = f"mariadb+mariadbconnector://{user}:{password}@{host}/{db}"  # pragma: allowlist secret
    sql_engine = sqlalchemy.create_engine(connect_string)

    query = """
    SELECT * FROM final_table
    """
    data = pd.DataFrame(sql_engine.connect().execute(text(query)))
    response = "Home_Team_Win"
    features = list(data.columns[4:-1])

    data = data.dropna()
    data = data.reset_index()

    print(features)
    print(data[response])
    for feature in features:
        data[feature] = data[feature].astype(float)
    data[response] = data[response].astype(bool)

    for feature in features:
        low, high = data[feature].quantile([0.05, 0.95])
        data[feature] = data[feature].clip(low, high)

    # dropping first few games since they will have the most skewed data for calculating stats such as BA
    # cutoff = int(len(data) * 0.05) Decided not to do it because new teams can join and whatnot so not based on date
    # data = data[cutoff:].reset_index()
    # print(data)
    # Midterm Feature Analysis

    midterm_stuff("Baseball", data, features, response)

    # My features seem good based on p-value and t-score. Almost too good.
    # All of them were below that 5% threshold with my WORST feature here being about 4.99%.
    # I will just fit a multivariate logistic model for now, but looking at correlations and MoR plots, I
    # will probably pick Pythag > Avg_Score_Diff, ISO > XBH, and a slight edge to CERA compared to OBA but both those
    # graphs seem extremely skewed

    # For train-test split, we cannot do a random split because the data is time-based.
    # The data is already sorted by local_date, so we can split it 80-20 directly
    model(data, features)

    """
    Clear example of overfitting. WHen I had 10 features, as per hw 5, I had a logistic AUC score of 0.52,
    but with 5 more predictors, a 50% increase, the AUC score has dropped to 0.51. Given the summary, we can
    drop Team Batting Average, diff_Score_Diff, diff_CERA, diff_Pythag, diff_WHIP, and diff_DIce. This leaves us
    with 9 features instead of 15.
    """
    print(data.head())
    new_data = data.drop(["diff_BA",
                          "diff_Score_Diff",
                          "diff_thrown",
                          "diff_CERA",
                          "diff_Pythag",
                          "diff_DICE"], axis=1)
    reduced_features = new_data.columns[4:-1]
    model(new_data, reduced_features)
    """
    Logistic Model went from 51  to 51.3. Random forest went up from 49.7 to 51.
    So small improvement, but now we drop highly correlated features. Which from Feature Analysis.html
    shows that XBH and ISO have a correlation of above 90%. Pythag and Score DIff are already dropped for this.
    Comparing their Mean of Response plots, ISO seems to be more helpful (probably due to the weights in
    calculations). ISO is doubles + 2*triples + 3*hr whereas XBH is just doubles+triples+HR.
    Also drop WHIP since p score about 33%. And if this goes well, maybe add knot point to ISO as well.
    """
    newer_data = new_data.drop(["diff_XBH", "diff_WHIP"], axis=1)
    reducer_features = newer_data.columns[4:-1]
    model(newer_data, reducer_features)
    """
        51.5 but now it looks like ISO is bad, so maybe drop that too. Or do the hinge point.
        Test hinge point first to see because it looks like there's a clear hinge point for that
        Mean of Response plot. Slope increases to the right
    """
    # newer_data["ISO_hinge"] = [max(0, i + 0.011) for i in newer_data["diff_ISO"].tolist()]
    # reducer_features = reducer_features[4:]
    # reducer_features = reducer_features.tolist().drop()
    # model(newer_data, reducer_features)
    # fourth_data = newer_data.drop(["diff_PTB", "diff_BABIP"], axis=1)
    # fourth_features = fourth_data.columns[3:-1]
    # model(fourth_data, fourth_features)

    return 0


if __name__ == "__main__":
    sys.exit(main())
