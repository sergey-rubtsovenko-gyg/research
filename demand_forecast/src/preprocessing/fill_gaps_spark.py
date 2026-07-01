from pyspark.sql import functions as F
from pyspark.sql import types as T # StringType
from pyspark.sql import Window

import pandas as pd
import numpy as np

from demand_forecast.src.spark_utils import spark


def fill_gaps_weekly(tour_week_sales_df, start_date, end_date):
    weekly_date_spine_df = get_weekly_date_spine(start_date, end_date)
    tour_id_df = tour_week_sales_df.select('tour_id').distinct()
    tour_week_timeseries_df = weekly_date_spine_df.crossJoin(tour_id_df)
    tour_week_timeseries_df = (
        tour_week_timeseries_df
        .join(tour_week_sales_df, on=['tour_id', 'date'], how='left')
        .withColumn('is_missing_date_imputed', F.when(F.col("tickets").isNull(), True).otherwise(False))
    )
    tour_week_timeseries_df = tour_week_timeseries_df.fillna(0, subset=["tickets"])
    return tour_week_timeseries_df


def get_weekly_date_spine(start_date, end_date):
    sql_query_template = """
            SELECT explode(sequence(
                next_day(date '{start_date}' - interval 7 days, 'Monday'),
                date '{end_date}',
                interval 7 days
            )) AS date
        """
    sql_query = sql_query_template.format(start_date=start_date, end_date=end_date)
    date_spine_df = spark.sql(sql_query)
    return date_spine_df
