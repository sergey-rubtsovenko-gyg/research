from pyspark.sql.types import IntegerType
import pyspark.sql.functions as F


def add_2(value):
    return value+2


udf_2 = F.udf(add_2, IntegerType())
