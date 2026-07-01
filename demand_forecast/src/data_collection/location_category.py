from demand_forecast.src.spark_utils import spark
from pyspark.sql import functions as F


def get_tour_location_category():
    location_df = spark.read.table('production.dwh.dim_location')
    location_df = location_df.select(
        'location_id',
        F.col('location_name').alias('location'),
        # 'city_name',
        # 'country_name',
    )

    tour_dim_df = spark.read.table('production.dwh.dim_tour')
    tour_dim_df = tour_dim_df.select(
        "tour_id",
        "location_id",
        F.col("category").alias('category_lvl1'),
        F.col("business_category_level_2").alias('category_lvl2'),
    )

    tour_location_category_df = tour_dim_df.join(location_df, 'location_id', 'left')
    tour_location_category_df = tour_location_category_df.withColumn(
        'location_cat_lvl2',
        F.concat_ws("_", F.col("location"), F.col("category_lvl2"))
    )
    return tour_location_category_df
