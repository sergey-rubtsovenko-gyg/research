from pyspark.sql import functions as F
from pyspark.sql import types as T # StringType
from pyspark.sql import Window


def fill_gaps(tour_day_sales_df, date_col, temporal_granularity):
    if temporal_granularity not in ("day", "week"):
        raise ValueError(f"temporal_granularity must be 'day' or 'week', received: '{temporal_granularity}'")

    tour_date_bounds_df = tour_day_sales_df.groupBy("tour_id").agg(
        F.min(date_col).cast("date").alias("min_date"),
        F.max(date_col).cast("date").alias("max_date"),
    )
    tour_date_spine_df = tour_date_bounds_df.select(
        "tour_id",
        F.explode(F.sequence("min_date", "max_date", F.expr(f"interval 1 {temporal_granularity}"))).alias(date_col),  # inclusive on both ends
    )
    tour_date_sales_no_gaps_df = tour_date_spine_df.join(tour_day_sales_df, on=["tour_id", date_col], how="left")
    tour_date_sales_no_gaps_df = tour_date_sales_no_gaps_df.withColumn(
        'is_missing_date_imputed',
        F.when(F.col("tickets").isNull(), True).otherwise(False)
    )
    tour_date_sales_no_gaps_df = tour_date_sales_no_gaps_df.fillna(0, subset=["tickets"])
    return tour_date_sales_no_gaps_df



def fill_gaps_end_date(tour_day_sales_df, date_col, temporal_granularity, end_date):
    if temporal_granularity not in ("day", "week"):
        raise ValueError(f"temporal_granularity must be 'day' or 'week', received: '{temporal_granularity}'")

    tour_date_bounds_df = tour_day_sales_df.groupBy("tour_id").agg(
        F.min(date_col).cast("date").alias("min_date"),
        # F.max(date_col).cast("date").alias("max_date"),
    )
    tour_date_bounds_df = tour_date_bounds_df.withColumn('max_date', F.lit(end_date).cast('date'))
    tour_date_spine_df = tour_date_bounds_df.select(
        "tour_id",
        F.explode(
            F.sequence(
                "min_date",                                                           # inclusive on left end
                F.col("max_date") - F.expr(f"interval 1 {temporal_granularity}"),     # exclusive on right end
                F.expr(f"interval 1 {temporal_granularity}")
            )
        ).alias(date_col),
    )
    tour_date_sales_no_gaps_df = tour_date_spine_df.join(tour_day_sales_df, on=["tour_id", date_col], how="left")
    tour_date_sales_no_gaps_df = tour_date_sales_no_gaps_df.withColumn(
        'is_missing_date_imputed',
        F.when(F.col("tickets").isNull(), True).otherwise(False)
    )
    tour_date_sales_no_gaps_df = tour_date_sales_no_gaps_df.fillna(0, subset=["tickets"])
    return tour_date_sales_no_gaps_df
