from pyspark.sql import functions as F
import pandas as pd
from datetime import date

# just get the spark object already created in databricks
from demand_forecast.src.spark_utils import spark


def get_start_end_dates_for_week_aligned(start_date, end_date):
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    week_aligned_start = start_ts - pd.Timedelta(days=start_ts.dayofweek)
    week_aligned_end = end_ts + pd.Timedelta(days=7 - end_ts.dayofweek)

    week_aligned_start = week_aligned_start.strftime('%Y-%m-%d')
    week_aligned_end = week_aligned_end.strftime('%Y-%m-%d')

    today = date.today().strftime('%Y-%m-%d')
    if today < week_aligned_end:
        raise ValueError(f'Today={today} is before week_aligned_end={week_aligned_end}')

    return week_aligned_start, week_aligned_end


def get_tour_option_time_slot_daily_sales(start_range_tour_date, end_range_tour_date):
    fact_booking_df = spark.table('production.dwh.fact_booking')
    fact_booking_df = (
        fact_booking_df
        .select(
            'tour_id',
            'tour_option_id',
            F.col('date_of_travel').alias('tour_ts_local'),
            F.col('date_of_checkout_local').alias('booking_ts_local'),
            'tickets',
            'status_id',
        )
        .withColumn('tour_ts', F.date_format('tour_ts_local', "yyyy-MM-dd HH:mm:ss"))
        .withColumn('tour_date', F.date_format('tour_ts_local', "yyyy-MM-dd"))
        .withColumn('tour_time', F.date_format('tour_ts_local', "HH:mm:ss"))
        .withColumn('booking_ts', F.date_format('booking_ts_local', "yyyy-MM-dd HH:mm:ss"))
        .withColumn('booking_date', F.date_format('booking_ts_local', "yyyy-MM-dd"))
        .withColumn('booking_time', F.date_format('booking_ts_local', "HH:mm:ss"))
        .drop('tour_ts_local', 'booking_ts_local')
    )

    status_df = spark.table('production.dwh.dim_status')
    status_df = (
        status_df
        .filter(F.col('status_name') == 'active')
        .select('status_id')
    )

    tour_option_time_slot_sales_df = (
        fact_booking_df
        .join(status_df, on='status_id', how='inner')
        .drop('status_id')
    )

    tour_option_time_slot_sales_df = (
        tour_option_time_slot_sales_df
        .filter(
            (F.col('tour_date') >= start_range_tour_date)
            & (F.col('tour_date') < end_range_tour_date)
        )
    )
    return tour_option_time_slot_sales_df


def filter_sales_after_activity_timestamp(tour_option_time_slot_sales_df):
    tour_option_time_slot_sales_df = (
        tour_option_time_slot_sales_df
        .filter(F.col('booking_ts') < F.col('activity_ts'))
    )
    return tour_option_time_slot_sales_df


def get_tour_option_daily_sales(tour_option_time_slot_sales_df):
    tour_option_daily_sales_df = (
        tour_option_time_slot_sales_df
        .groupby('tour_id', 'tour_option_id', 'tour_date').agg(
            F.sum('tickets').alias('tickets'),
        )
    )
    return tour_option_daily_sales_df


def get_tour_daily_sales(tour_option_daily_sales_df):
    tour_daily_sales_df = tour_option_daily_sales_df.groupby('tour_id', 'tour_date').agg(
        F.sum('tickets').alias('tickets'),
    )
    return tour_daily_sales_df


def get_tour_weekly_sales(tour_option_time_slot_sales_df):
    tour_weekly_sales_df = (
        tour_option_time_slot_sales_df
        .withColumn("tour_week_start_date", F.date_trunc("week", F.col("tour_date")).cast("date")) # start date of the week
        # .withColumn('activity_week', F.date_format('activity_week', "yyyy-MM-dd"))
        .groupby('tour_id', 'tour_week_start_date').agg(
            F.sum('tickets').alias('tickets'),
        )
    )
    return tour_weekly_sales_df
