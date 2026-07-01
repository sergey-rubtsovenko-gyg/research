from pyspark.sql import functions as F
from pyspark.sql import types as T # StringType
from pyspark.sql import Window
import pandas as pd
from datetime import date
from demand_forecast.src.spark_utils import spark


def get_tour_week_scaling_factor(tour_week_sales_df):
    tour_week_sales_df = tour_week_sales_df.withColumn('date', F.col('tour_week_start_date'))

    w_lag = Window.partitionBy("tour_id").orderBy("date")
    tour_week_sales_df = tour_week_sales_df.withColumn(
        'tickets_lag1y',
        F.lag("tickets", 52).over(w_lag)
    )

    tour_week_sales_df.createOrReplaceTempView("tour_week_sales_df")

    scaling_factor_df = spark.sql("""
    SELECT
        pivot_dates.tour_id
        , pivot_dates.date AS pivot_date
        , prev_dates.date AS date
        , ROUND(
            LEAST(1 / ceil(DATEDIFF(DAY, prev_dates.date, pivot_dates.date) / 30), 1), 
            2
        ) AS weight
        , prev_dates.tickets
        , prev_dates.tickets_lag1y
    FROM tour_week_sales_df AS pivot_dates
    LEFT JOIN tour_week_sales_df AS prev_dates ON 
        pivot_dates.tour_id = prev_dates.tour_id
        AND prev_dates.date >= pivot_dates.date - INTERVAL '1 year' 
        AND prev_dates.date <= pivot_dates.date 
    WHERE 
        prev_dates.tickets_lag1y IS NOT NULL
    ORDER BY
        tour_id
        , pivot_date
        , date
    """)

    scaling_factor_df = (
        scaling_factor_df
        .groupBy('tour_id', 'pivot_date').agg(
            (
                F.sum(F.col('tickets') * F.col('weight'))
                / F.sum(F.col('tickets_lag1y') * F.col('weight'))
            ).alias('scaling_factor_unconstrained')
        )
        .withColumn('scaling_factor_clip_1_5', F.least(F.col('scaling_factor_unconstrained'), F.lit(1.5)))
        .withColumn('scaling_factor_clip_2_0', F.least(F.col('scaling_factor_unconstrained'), F.lit(2.0)))
        .withColumn('scaling_factor_clip_2_5', F.least(F.col('scaling_factor_unconstrained'), F.lit(2.5)))
        .withColumn('scaling_factor_clip_3_0', F.least(F.col('scaling_factor_unconstrained'), F.lit(3.0)))
        .withColumn('scaling_factor', F.least(F.col('scaling_factor_unconstrained'), F.lit(2.5)))
        .withColumnRenamed('pivot_date', 'date')
    )

    tour_week_sales_with_factor_df = tour_week_sales_df.join(scaling_factor_df, on=['tour_id', 'date'], how='left')

    w_lag = Window.partitionBy("tour_id").orderBy("date")
    tour_week_sales_with_factor_df = (
        tour_week_sales_with_factor_df
        .withColumn(
            'scaling_factor_lag4w',
            F.lag("scaling_factor", 4).over(w_lag)
        )
        .withColumn(
            'scaling_factor_lag8w',
            F.lag("scaling_factor", 8).over(w_lag)
        )
        .withColumn(
            'scaling_factor_lag12w',
            F.lag("scaling_factor", 12).over(w_lag)
        )
    )
    tour_week_sales_with_factor_df = tour_week_sales_with_factor_df.drop('date')
    return tour_week_sales_with_factor_df
