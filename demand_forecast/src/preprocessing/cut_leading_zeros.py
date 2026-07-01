from pyspark.sql import functions as F
from pyspark.sql import types as T # StringType
from pyspark.sql import Window


def cut_leading_zeros(timeseries_df, date_col='date'):
    tour_first_date_with_sales_df = (
        timeseries_df
        .filter(F.col("tickets") != 0)
        .groupBy("tour_id")
        .agg(F.min(date_col).alias("first_date_with_sales"))
    )

    df = timeseries_df.join(tour_first_date_with_sales_df, on='tour_id', how='inner')
    df = df.filter(F.col('tour_week') >= F.col('first_date_with_sales'))
    return df
