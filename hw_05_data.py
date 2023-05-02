import pandas as pd
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

import transformer as t


# spark.apache.org/docs/latest/sql-data-sources-jdbc.html helped me load in data in spark.
# A lot of the other stuff was from the TA helping me out
def data_loader(password):
    driver = "org.mariadb.jdbc.Driver"
    url = "jdbc:mysql://localhost:3306/baseball?permitMysqlScheme"
    spark = SparkSession.builder.getOrCreate()
    tba = (
        spark.read.format("jdbc")
        .option("url", url)
        .option("dbtable", "baseball.team_ba")
        .option("user", "root")
        .option("password", password)
        .option("driver", driver)
        .load()
    )

    tba = tba.withColumn("local_date", tba.local_date.cast("timestamp"))
    trans_bat = t.BattingAverageTransformer(
        inputCols=["team_id", "local_date", "Hits", "atBats"], outputCol="BA"
    )
    trans_oba = t.BattingAverageTransformer(
        inputCols=["team_id", "local_date", "opp_hits", "opp_AB"], outputCol="AVG_OBA"
    )
    trans_XBH = t.AvgTransformer(
        inputCols=["team_id", "local_date", "XBH"], outputCol="AVG_XBH"
    )
    trans_score_diff = t.AvgTransformer(
        inputCols=["team_id", "local_date", "Score_Diff"], outputCol="AVG_Score_Diff"
    )
    trans_innpitch = t.AvgTransformer(
        inputCols=["team_id", "local_date", "innings_pitched"], outputCol="AVG_INN_P"
    )
    trans_pt = t.AvgTransformer(
        inputCols=["team_id", "local_date", "thrown"], outputCol="AVG_PT"
    )
    cera = t.CERA(
        inputCols=[
            "opp_hits",
            "walks",
            "HBP",
            "opp_HR",
            "intent_walk",
            "plate_appearance",
            "innings_pitched",
            "team_id",
            "local_date",
        ],
        outputCol="Team_CERA",
    )
    pythag = t.Pythag(
        inputCols=["team_id", "local_date", "runs", "opp_runs"], outputCol="Pythag"
    )
    iso = t.ISO(
        inputCols=["team_id", "local_date", "Doubles", "Triples", "HR", "atBats"],
        outputCol="AVG_ISO",
    )
    ops = t.OPS(
        inputCols=[
            "team_id",
            "local_date",
            "Hits",
            "walks",
            "HBP",
            "atBats",
            "Sac_Fly",
        ],
        outputCol="AVG_OPS",
    )
    pipeline = Pipeline(
        stages=[
            trans_bat,
            trans_oba,
            trans_XBH,
            trans_score_diff,
            trans_innpitch,
            trans_pt,
            cera,
            pythag,
            iso,
            ops,
        ]
    )
    model = pipeline.fit(tba)

    # print(type(team_stats.toPandas()))

    ps = (
        spark.read.format("jdbc")
        .option("url", url)
        .option("dbtable", "baseball.pitch_stats")
        .option("user", "root")
        .option("password", password)
        .option("driver", driver)
        .load()
    )
    team_stats_wp = tba.join(ps, ["team_id", "game_id"], "inner")
    # team_stats_wp.show()

    team_stats = model.transform(team_stats_wp)

    df1 = team_stats.select(
        col("team_id"),
        col("game_id"),
        col("local_date"),
        # Feature 0
        col("BA"),  # Feature 1 Batting Average
        col("AVG_OBA"),  # Feature 2 Oppnent Batting Avg
        col("AVG_XBH"),  # Feature 3 eXtra Base Hits
        col("AVG_Score_Diff"),  # Feature 4
        col("AVG_INN_P"),  # Feature 5 Innings Pitched
        col("AVG_PT"),  # Feature 6 Pitches Thrown
        col("Team_CERA"),  # Feature 7 CERA score for team starting pitcher
        col("Pythag"),  # Feature 8 The pythagoean win percentage
        col("AVG_ISO"),  # Feature 9, Isolated power
        col("AVG_OPS"),  # Feature 10, on base plus sluggings
        col("Home_Team_Win"),  # Response
    ).where(team_stats["home_team"] == 1)

    df2 = team_stats.select(
        col("team_id").alias("opp_team_id"),
        col("game_id"),
        # Feature 0
        col("BA").alias("opp_BA"),  # Feature 1 Batting Average
        col("AVG_OBA").alias("opp_AVG_OBA"),  # Feature 2 Oppnent Batting Avg
        col("AVG_XBH").alias("opp_AVG_XBH"),  # Feature 3 eXtra Base Hits
        col("AVG_Score_Diff").alias("opp_AVG_Score_Diff"),  # Feature 4
        col("AVG_INN_P").alias("opp_AVG_INN_P"),  # Feature 5 Innings Pitched
        col("AVG_PT").alias("opp_AVG_PT"),  # Feature 6 Pitches Thrown
        col("Team_CERA").alias(
            "opp_Team_CERA"
        ),  # Feature 7 CERA score for team starting pitcher
        col("Pythag").alias("opp_Pythag"),  # Feature 8 The pythagoean win percentage
        col("AVG_ISO").alias("opp_AVG_ISO"),  # Feature 9, Isolated power
        col("AVG_OPS").alias("opp_AVG_OPS"),  # Feature 10, on base plus sluggings
    ).where(team_stats["home_team"] == 0)

    df = df1.join(df2, ["game_id"], "inner")
    df = (
        df.withColumn("diff_BA", df["BA"] - df["opp_BA"])
        .withColumn("diff_OBA", df["AVG_OBA"] - df["opp_AVG_OBA"])
        .withColumn("diff_XBH", df["AVG_XBH"] - df["opp_AVG_XBH"])
        .withColumn("diff_Score_Diff", df["AVG_Score_Diff"] - df["opp_AVG_Score_Diff"])
        .withColumn("diff_INN_P", df["AVG_INN_P"] - df["opp_AVG_INN_P"])
        .withColumn("diff_PT", df["AVG_PT"] - df["opp_AVG_PT"])
        .withColumn("diff_CERA", df["Team_CERA"] - df["opp_Team_CERA"])
        .withColumn("diff_Pythag", df["Pythag"] - df["opp_Pythag"])
        .withColumn("diff_ISO", df["AVG_ISO"] - df["opp_AVG_ISO"])
        .withColumn("diff_OPS", df["AVG_OPS"] - df["opp_AVG_OPS"])
    )

    df = df.select(
        col("team_id"),
        col("opp_team_id"),
        col("game_id"),
        col("local_date"),
        col("diff_BA"),
        col("diff_OBA"),
        col("diff_XBH"),
        col("diff_Score_Diff"),
        col("diff_INN_P"),
        col("diff_PT"),
        col("diff_CERA"),
        col("diff_Pythag"),
        col("diff_ISO"),
        col("diff_OPS"),
        col("Home_Team_Win"),
    )
    # df.show()
    df.write.format("jdbc").mode("overwrite").option("url", url).option(
        "user", "root"
    ).option("dbtable", "df_with_features").option("password", password).save()
    df = df.toPandas()
    df = df.astype(
        {
            "team_id": str,
            "opp_team_id": str,
            "game_id": str,
            "local_date": str,
            "diff_BA": float,
            "diff_OBA": float,
            "diff_XBH": float,
            "diff_Score_Diff": float,
            "diff_INN_P": float,
            "diff_PT": float,
            "diff_CERA": float,
            "diff_Pythag": float,
            "diff_ISO": float,
            "diff_OPS": float,
            "Home_Team_Win": int,
        }
    )
    df = pd.DataFrame(df)
    df["local_date"] = pd.to_datetime(df["local_date"], infer_datetime_format=True)
    data = df.sort_values("local_date")
    features = df.columns[4:-1].to_list()
    response = df.columns[-1]

    return data, features, response
