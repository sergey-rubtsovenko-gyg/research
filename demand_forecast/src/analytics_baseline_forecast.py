from pyspark.sql import functions as F
from pyspark.sql import types as T # T.StringType
from pyspark.sql import Window
from demand_forecast.src.spark_utils import spark


def get_analytics_baseline_forecast_one_snapshot(forecast_created_date, start_range_tour_date, end_range_tour_date):
    accuracy_baseline_snapshot_df = spark.table('production.supply_analytics.demand_forecast_accuracy')

    accuracy_baseline_snapshot_df = (
        accuracy_baseline_snapshot_df
        .select(
            F.col("forecast_date").alias("forecast_created_date"),
            F.col('travel_date').alias("tour_date"),
            "tour_id",
            "growth_rate",
            F.col('forecast_tickets_sold').alias("tickets_forecast"),
            F.col('actual_tickets_sold').alias('tickets_actual')
        )
    )

    accuracy_baseline_snapshot_df = (
        accuracy_baseline_snapshot_df
        .filter(F.col('forecast_created_date') == forecast_created_date)
        .filter(
            (F.col('tour_date') >= start_range_tour_date)
            & (F.col('tour_date') < end_range_tour_date)
        )
    )

    return accuracy_baseline_snapshot_df


def get_analytics_baseline_forecast(snapshot_dates_df, start_range_tour_date, end_range_tour_date):
    baseline_snapshots_df = spark.table('production.supply_analytics.demand_forecast_accuracy')

    baseline_snapshots_df = (
        baseline_snapshots_df
        .select(
            F.col("forecast_date").alias("forecast_created_date"),
            F.col('travel_date').alias("tour_date"),
            "tour_id",
            "growth_rate",
            F.col('forecast_tickets_sold').alias("tickets_forecast"),
            F.col('actual_tickets_sold').alias('tickets_actual')
        )
    )

    baseline_snapshots_df = (
        baseline_snapshots_df
        .join(snapshot_dates_df, on='forecast_created_date', how='inner')
        .filter(
            (F.col('tour_date') >= start_range_tour_date)
            & (F.col('tour_date') < end_range_tour_date)
        )
    )

    return baseline_snapshots_df


def get_snapshot_dates_df():
    accuracy_baseline_snapshot_df = spark.table('production.supply_analytics.demand_forecast_accuracy')

    accuracy_baseline_snapshot_df = (
        accuracy_baseline_snapshot_df
        .select(
            F.col("forecast_date").alias("forecast_created_date"),
            F.col('travel_date').alias("tour_date"),
            "tour_id",
            F.col('forecast_tickets_sold').alias("forecast"),
            F.col('actual_tickets_sold').alias('tickets')
        )
    )

    snapshot_dates_df = (
        accuracy_baseline_snapshot_df
        .select('forecast_created_date')
        .distinct()
        .sort("forecast_created_date")
    )

    return snapshot_dates_df


def get_monthly_snapshots(start_date, end_date):
    snapshot_dates_df = get_snapshot_dates_df()
    snapshot_dates_df = (
        snapshot_dates_df
        .filter(
            (F.col('forecast_created_date') >= start_date)
            & (F.col('forecast_created_date') < end_date)
        )
    )

    snapshot_dates_df = (
        snapshot_dates_df
        .withColumn('snapshot_year', F.year('forecast_created_date'))
        .withColumn('snapshot_month', F.month('forecast_created_date'))
    )

    w = Window.partitionBy('snapshot_year', 'snapshot_month').orderBy(F.col('forecast_created_date').desc())
    monthly_snapshots_dates_df = (
        snapshot_dates_df
        .withColumn('rn', F.row_number().over(w))
        .filter(F.col('rn') == 1)
        .drop('rn')
    )

    return monthly_snapshots_dates_df
