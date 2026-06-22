from pyspark.sql import functions as F
from demand_forecast.src.spark_utils import spark


def get_analytics_baseline_forecast(forecast_created_date, start_range_tour_date, end_range_tour_date):
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

    accuracy_baseline_snapshot_df = (
        accuracy_baseline_snapshot_df
        .filter(F.col('forecast_created_date') == forecast_created_date)
        .filter(
            (F.col('tour_date') >= start_range_tour_date)
            & (F.col('tour_date') < end_range_tour_date)
        )
    )

    return accuracy_baseline_snapshot_df


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