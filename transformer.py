import pyspark.sql.functions as F
from pyspark import keyword_only
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCols, HasOutputCol
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql.functions import col
from pyspark.sql.window import Window


def days(i):
    return i * 86400


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
        w = (
            Window()
            .partitionBy(input_cols[0])
            .orderBy(col(input_cols[1]).cast("long"))
            .rangeBetween(-days(101), -1)
        )
        # Generate a list of columns to append
        dataset = dataset.withColumn(
            output_col,
            F.sum(col(input_cols[-2])).over(w) / F.sum(col(input_cols[-1])).over(w),
        )
        dataset = dataset.fillna({output_col: "0"})
        return dataset
