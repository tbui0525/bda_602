import sys

from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

import transformer as t

# import pandas as pd


# spark.apache.org/docs/latest/sql-data-sources-jdbc.html helped me load in data in spark.
# A lot of the other stuff was from the TA helping me out
def main():
    driver = "org.mariadb.jdbc.Driver"
    url = "jdbc:mysql://localhost:3306/baseball?permitMysqlScheme"
    password = input("Password: ")
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

    df = team_stats.select(
        col("team_id"),
        col("game_id"),
        col("local_date"),
        col("home_team"),  # Feature 0
        col("BA"),  # Feature 1 Batting Average
        col("AVG_OBA"),  # Feature 2 Oppnent Batting Avg
        col("AVG_XBH"),  # Feature 3 eXtra Base Hits
        col("Avg_Score_Diff"),  # Feature 4
        col("AVG_INN_P"),  # Feature 5 Innings Pitched
        col("AVG_PT"),  # Feature 6 Pitches Thrown
        col("Team_CERA"),  # Feature 7 CERA score for team starting pitcher
        col("Pythag"),  # Feature 8 The pythagoean win percentage
        col("AVG_ISO"),  # Feature 9, Isolated power
        col("AVG_OPS"),  # Feature 10, on base plus sluggings
        col("Home_Team_Win"),  # Response
    )

    df.show()
    return 0


if __name__ == "__main__":
    sys.exit(main())
