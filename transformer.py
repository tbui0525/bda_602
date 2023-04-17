import pyspark.sql.functions as F
from pyspark import keyword_only
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCols, HasOutputCol
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql.functions import col
from pyspark.sql.window import Window


def days(i):
    return i * 86400


def w(input_cols):
    return (
        Window()
        .partitionBy(input_cols[0])
        .orderBy(col(input_cols[1]).cast("long"))
        .rangeBetween(-days(101), -1)
    )


# Most of this actually came from your lecture notes Julien
class BattingAverageTransformer(
    Transformer,
    HasInputCols,
    HasOutputCol,
    DefaultParamsReadable,
    DefaultParamsWritable,
):
    @keyword_only
    def __init__(self, inputCols=None, outputCol=None):
        super(BattingAverageTransformer, self).__init__()
        kwargs = self._input_kwargs
        self.setParams(**kwargs)
        return

    @keyword_only
    def setParams(self, inputCols=None, outputCol=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _transform(self, dataset):
        input_cols = self.getInputCols()
        output_col = self.getOutputCol()
        # https://stackoverflow.com/questions/45806194/pyspark-rolling-average-using-timeseries-data

        # I tried to just make a window function but that failed so I had to retype it each time
        wdw = w(input_cols)

        # Generate a list of columns to append
        dataset = dataset.withColumn(
            output_col,
            F.sum(col(input_cols[-2])).over(wdw) / F.sum(col(input_cols[-1])).over(wdw),
        )
        dataset = dataset.fillna({output_col: "0"})
        return dataset


class AvgTransformer(
    Transformer,
    HasInputCols,
    HasOutputCol,
    DefaultParamsReadable,
    DefaultParamsWritable,
):
    @keyword_only
    def __init__(self, inputCols=None, outputCol=None):
        super(AvgTransformer, self).__init__()
        kwargs = self._input_kwargs
        self.setParams(**kwargs)
        return

    @keyword_only
    def setParams(self, inputCols=None, outputCol=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _transform(self, dataset):
        input_cols = self.getInputCols()
        output_col = self.getOutputCol()
        # https://stackoverflow.com/questions/45806194/pyspark-rolling-average-using-timeseries-data
        wdw = w(input_cols)
        # Generate a list of columns to append
        dataset = dataset.withColumn(
            output_col,
            F.avg(input_cols[-1]).over(wdw),
        )
        dataset = dataset.fillna({output_col: "0"})
        return dataset


class CERA(
    Transformer,
    HasInputCols,
    HasOutputCol,
    DefaultParamsReadable,
    DefaultParamsWritable,
):
    @keyword_only
    def __init__(self, inputCols=None, outputCol=None):
        super(CERA, self).__init__()
        kwargs = self._input_kwargs
        self.setParams(**kwargs)
        return

    @keyword_only
    def setParams(self, inputCols=None, outputCol=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _transform(self, dataset):
        input_cols = self.getInputCols()
        output_col = self.getOutputCol()
        # https://stackoverflow.com/questions/45806194/pyspark-rolling-average-using-timeseries-data
        wdw = (
            Window()
            .partitionBy(input_cols[-2])
            .orderBy(col(input_cols[-1]).cast("long"))
            .rangeBetween(-days(101), -1)
        )
        # Generate a list of columns to append
        dataset = dataset.withColumn(
            output_col,
            # CERA EQUATION FROM WIKIPEDIA
            9
            * (
                F.sum(col(input_cols[0])).over(wdw)
                + F.sum(col(input_cols[1])).over(wdw)
                + F.sum(col(input_cols[2])).over(wdw)
            )
            * (
                0.89
                * (
                    1.255
                    * (
                        F.sum(col(input_cols[0])).over(wdw)
                        - F.sum(col(input_cols[3])).over(wdw)
                    )
                    + 4 * F.sum(col(input_cols[3])).over(wdw)
                )
                + 0.56
                * (
                    F.sum(col(input_cols[1])).over(wdw)
                    + F.sum(col(input_cols[2])).over(wdw)
                    - F.sum(col(input_cols[4])).over(wdw)
                )
            )
            / (
                F.sum(col(input_cols[5])).over(wdw)
                * F.sum(col(input_cols[6])).over(wdw)
            )
            - 0.56,
        )
        dataset = dataset.fillna({output_col: "0"})
        return dataset


class Pythag(
    Transformer,
    HasInputCols,
    HasOutputCol,
    DefaultParamsReadable,
    DefaultParamsWritable,
):
    @keyword_only
    def __init__(self, inputCols=None, outputCol=None):
        super(Pythag, self).__init__()
        kwargs = self._input_kwargs
        self.setParams(**kwargs)
        return

    @keyword_only
    def setParams(self, inputCols=None, outputCol=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _transform(self, dataset):
        input_cols = self.getInputCols()
        output_col = self.getOutputCol()
        # https://stackoverflow.com/questions/45806194/pyspark-rolling-average-using-timeseries-data
        wdw = w(input_cols)
        # Generate a list of columns to append
        dataset = dataset.withColumn(
            output_col,
            F.sum(col(input_cols[2])).over(wdw) ** 2
            / (  # runs scored squared
                F.sum(col(input_cols[2])).over(wdw) ** 2
                + F.sum(col(input_cols[3])).over(wdw) ** 2
            ),
        )
        dataset = dataset.fillna({output_col: "0"})
        return dataset


class ISO(
    Transformer,
    HasInputCols,
    HasOutputCol,
    DefaultParamsReadable,
    DefaultParamsWritable,
):
    @keyword_only
    def __init__(self, inputCols=None, outputCol=None):
        super(ISO, self).__init__()
        kwargs = self._input_kwargs
        self.setParams(**kwargs)
        return

    @keyword_only
    def setParams(self, inputCols=None, outputCol=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _transform(self, dataset):
        input_cols = self.getInputCols()
        output_col = self.getOutputCol()
        # https://stackoverflow.com/questions/45806194/pyspark-rolling-average-using-timeseries-data

        # I tried to just make a window function but that failed so I had to retype it each time
        wdw = w(input_cols)

        # Generate a list of columns to append
        dataset = dataset.withColumn(
            output_col,
            (
                F.sum(col(input_cols[2])).over(wdw)
                + 2 * F.sum(col(input_cols[3])).over(wdw)  # doubles
                + 3 * F.sum(col(input_cols[4])).over(wdw)  # triples
            )  # home runs
            / F.sum(col(input_cols[-1])).over(wdw),  # atBats
        )
        dataset = dataset.fillna({output_col: "0"})
        return dataset


class OPS(
    Transformer,
    HasInputCols,
    HasOutputCol,
    DefaultParamsReadable,
    DefaultParamsWritable,
):
    @keyword_only
    def __init__(self, inputCols=None, outputCol=None):
        super(OPS, self).__init__()
        kwargs = self._input_kwargs
        self.setParams(**kwargs)
        return

    @keyword_only
    def setParams(self, inputCols=None, outputCol=None):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _transform(self, dataset):
        input_cols = self.getInputCols()
        output_col = self.getOutputCol()
        # https://stackoverflow.com/questions/45806194/pyspark-rolling-average-using-timeseries-data

        # I tried to just make a window function but that failed so I had to retype it each time
        wdw = w(input_cols)

        # Generate a list of columns to append
        dataset = dataset.withColumn(
            output_col,
            (
                F.sum(col(input_cols[2])).over(wdw)
                + F.sum(col(input_cols[3])).over(wdw)  # Hits
                + F.sum(col(input_cols[4])).over(wdw)  # Walks
            )  # HBP
            / (
                F.sum(col(input_cols[5])).over(wdw)
                + F.sum(col(input_cols[2])).over(wdw)
                + F.sum(col(input_cols[6])).over(wdw)  # Walks
                + F.sum(col(input_cols[4])).over(wdw)  # Sac Fly  # HBP
            ),  # atBats
        )
        dataset = dataset.fillna({output_col: "0"})
        return dataset
