from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.types import StringType
from pyspark.sql import Window
import pandas as pd
import numpy as np
from datetime import date


def keep_only_online_status_change_events(df, today_date):
    w = Window.partitionBy("tour_id").orderBy(F.col("update_timestamp"))

    df = (
        df
        .withColumn('prev_is_online', F.lag('is_online').over(w))
        .withColumn('record_rank', F.row_number().over(w))
        .filter(
            (F.col('is_online') != F.col('prev_is_online'))
            | (F.col('record_rank') == 1)
        )
        .withColumn("update_timestamp_next", F.lead("update_timestamp").over(w))
        .withColumn(
            "update_timestamp_next",
            F.coalesce(F.col('update_timestamp_next'), F.lit(today_date)).cast('timestamp_ntz')
        )
    )

    df = df.select(
        'tour_id',
        'is_online',
        'prev_is_online',
        'user_status',
        'gyg_status',
        'update_timestamp',
        "update_timestamp_next",
        'date_of_creation',
        'date_of_first_online',
        'dbz_timestamp',
    )

    return df


def get_tour_date_availability_date_range(spark, df, start_date, end_date):
    date_spine_df = spark.range(1).select(
        F.explode(
            F.sequence(F.lit(start_date).cast("date"), F.lit(end_date).cast("date"))
        ).alias("date")
    )
    tours_spine_df = df.select('tour_id').distinct()
    tour_date_spine_df = tours_spine_df.crossJoin(date_spine_df)

    today_date = date.today()
    df = keep_only_online_status_change_events(df, today_date)

    online_minutes_intervals_df = (
        df
        .withColumn("date", F.explode(
            F.sequence(F.to_date("update_timestamp"), F.to_date("update_timestamp_next"))
        ))
        .withColumn(
            "day_start",
            F.greatest(
                F.col("update_timestamp"),
                F.col("date").cast("timestamp")
            ).cast("timestamp")
        )
        .withColumn(
            "day_end",
            F.least(
                F.col("update_timestamp_next"),
                F.date_add(F.col("date"), 1).cast("timestamp")
            ).cast("timestamp")
        )
        .withColumn(
            "minutes",
            (F.unix_timestamp("day_end") - F.unix_timestamp("day_start")) / 60
        )
        .filter(F.col('date') != today_date)
    )

    online_minutes_df = (
        online_minutes_intervals_df
        .groupBy("tour_id", "date")
        .agg(F.sum(F.when(F.col("is_online"), F.col("minutes")).otherwise(0)).alias("online_minutes"))
        .withColumn('time_online_share', F.round(F.col('online_minutes') / (24 * 60), 5))
    )

    tour_date_availability_df = (
        tour_date_spine_df
        .join(online_minutes_df, on=["tour_id", "date"], how="left")
        .fillna(0, subset=["online_minutes", "time_online_share"])
    )

    # return date_spine
    return tour_date_availability_df
