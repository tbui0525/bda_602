import sys

from pyspark import StorageLevel
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

from transformer import BattingAverageTransformer


# spark.apache.org/docs/latest/sql-data-sources-jdbc.html helped me load in data in spark.
# A lot of the other stuff was from the TA helping me out
def main():
    driver = "org.mariadb.jdbc.Driver"
    url = "jdbc:mysql://localhost:3306/baseball?permitMysqlScheme"
    password = input("Password: ")
    spark = SparkSession.builder.getOrCreate()
    bc = (
        spark.read.format("jdbc")
        .option("url", url)
        .option("dbtable", "baseball.batter_counts")
        .option("user", "root")
        .option("password", password)
        .option("driver", driver)
        .load()
    )
    bc.persist(StorageLevel.MEMORY_ONLY)
    game = (
        spark.read.format("jdbc")
        .option("url", url)
        .option("dbtable", "baseball.game")
        .option("user", "root")
        .option("password", password)
        .option("driver", driver)
        .load()
    )
    game.persist(StorageLevel.MEMORY_ONLY)
    joined = bc.join(game, ["game_id"], "inner")
    each_day = joined.select(
        col("batter"), col("game_id"), col("local_date"), col("Hit"), col("atBat")
    )
    each_day = each_day.withColumn("local_date", each_day.local_date.cast("timestamp"))
    ba_trans = BattingAverageTransformer(
        inputCols=["batter", "local_date", "Hit", "atBat"], outputCol="BA"
    )
    pipeline = Pipeline(stages=[ba_trans])
    model = pipeline.fit(each_day)
    ba = model.transform(each_day)
    ba.show()

    spark.stop()
    return


if __name__ == "__main__":
    sys.exit(main())
