import sys

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
import pandas as pd
import sqlalchemy

from midterm import midterm_stuff


def main():
    user = "root"
    password = "jIg688xaj?"  # pragma: allowlist secret
    #git host = "localhost"
    host = "mariadb"
    db = "baseball"
    connect_string = f"mariadb+mariadbconnector://{user}:{password}@{host}/{db}"  # pragma: allowlist secret
    sql_engine = sqlalchemy.create_engine(connect_string)

    query = """
    SELECT * FROM final_table
    """
    data = pd.read_sql_query(query, sql_engine)
    response = "Home_Team_Win"
    features = list(data.columns[3:-1])

    data = data.dropna()
    data = data.reset_index()
    print(features)
    print(data[response])
    lower_percentile = 0.05,
    higher_percentile = 0.95


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

    split_point = int(len(data) * 0.8)  # creates split point for train-test
    print(split_point)
    train_data = data[:split_point]  # everything up to split point
    y_train = train_data["Home_Team_Win"]
    x_train = train_data[features]
    test_data = data[split_point:]  # everything from split point
    y_test = test_data["Home_Team_Win"]
    x_test = test_data[features]
    logreg_model = LogisticRegression(random_state=69).fit(x_train, y_train)
    #print(logreg_model.summary())
    y_log_pred = logreg_model.predict(x_test)
    log_roc_auc = roc_auc_score(y_test, y_log_pred)
    log_cr = classification_report(y_test, y_log_pred)
    # Using AUC to evaluate model instead of just accuracy or precision.
    print("Logistic ROC AUC Score: ", log_roc_auc)
    print("Logistic Class Report")
    print(log_cr)
    forest = RandomForestClassifier(n_estimators=100, random_state=69)
    forest.fit(x_train, y_train)
    y_rf_pred = forest.predict(x_test)
    rf_roc_auc = roc_auc_score(y_test, y_rf_pred)
    rf_cr = classification_report(y_test, y_rf_pred)
    print("Random Forest ROC AUC Score: ", rf_roc_auc)
    print("Random Forest Class Report")
    print(rf_cr)
    """
    I'll be editing this for the final to make the model better. I am assuming high levels of overfitting
    because of the high level of correlations between variables as can be seen in the Feature Analysis.html.
    Given the time constraint. I'll settle for this for the hw. Speed > Best Model to get funding right? ;P
    I'll also set an outlier check so if it's below the bottom 10%, move it up to the 10% mark and if
    above 90%, move it down to 90% mark for all features. Or 5% and 95%. Will have to test to find out.
    Clipping the data that way may result in different features being more important as well.
    Currently, the better of the two models is the logistic regression which is slightly better than a coin flip.
    """

    return 0


if __name__ == "__main__":
    sys.exit(main())
