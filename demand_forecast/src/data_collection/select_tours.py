from dateutil.relativedelta import relativedelta
from datetime import datetime
import textwrap
from pyspark.sql import functions as F

from demand_forecast.src.data_collection.tour_sales import (
    get_tour_option_time_slot_daily_sales,
    get_tour_daily_sales,
)
from demand_forecast.src.spark_utils import spark


def select_regular_tours(
    end_date,
    n_years=3,
    n_months_buffer=6,
    avg_tickets_per_day=10,
    days_with_sales_share=0,
):
    start_date = (
        datetime.strptime(end_date, "%Y-%m-%d")
        - relativedelta(years=n_years)
        - relativedelta(months=n_months_buffer)
    ).strftime("%Y-%m-%d")

    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")

    tour_option_time_slot_sales_df = get_tour_option_time_slot_daily_sales(
        start_range_tour_date=start_date,
        end_range_tour_date=end_date,
    )
    tour_daily_sales_df = get_tour_daily_sales(tour_option_time_slot_sales_df)

    tour_daily_sales_df.createOrReplaceTempView("tour_daily_sales")

    sql_query_template = textwrap.dedent(f"""
        WITH tmp AS (
            SELECT
                tour_id
                , MIN(DATE(tour_date))                               AS first_tour_date
                , MAX(DATE(tour_date))                               AS last_tour_date
                , DATEDIFF(
                    MAX(DATE(tour_date)),
                    MIN(DATE(tour_date))
                )                                                    AS days_between_first_and_last_tour_date
                , COUNT(DISTINCT DATE(tour_date))                    AS n_dates_with_sales
                , SUM(tickets)                                       AS tickets
                , ROUND(AVG(tickets), 2)                             AS avg_tickets_per_day
            FROM tour_daily_sales
            GROUP BY tour_id
        )
        
        , tmp_2 AS (
            SELECT
                tmp.tour_id
                , first_tour_date
                , last_tour_date
                , days_between_first_and_last_tour_date
                , n_dates_with_sales
                , tickets
                , avg_tickets_per_day
                , ROUND(n_dates_with_sales / days_between_first_and_last_tour_date, 2) AS days_with_sales_share
            FROM tmp
        )

        SELECT
            tour_id
            , first_tour_date
            , last_tour_date
            , days_between_first_and_last_tour_date
            , n_dates_with_sales
            , tickets
            , avg_tickets_per_day
            , days_with_sales_share
            , '{start_date}' AS _start_date
            , '{end_date}' AS _end_date
            , current_timestamp() AS _created_ts
        FROM tmp_2
        WHERE days_between_first_and_last_tour_date >= {n_years} * 365
            AND avg_tickets_per_day > {avg_tickets_per_day}
            AND days_with_sales_share >= {days_with_sales_share}
    """)

    sql_query = sql_query_template.format(
        start_date=start_date,
        end_date=end_date,
        n_years=n_years,
        avg_tickets_per_day=avg_tickets_per_day,
        days_with_sales_share=days_with_sales_share,
    )

    selected_tours_df = spark.sql(sql_query)

    return selected_tours_df


def select_trending_tours(
    end_date,
    target_year,
    min_growth=0.3,
    min_sales_prev_year=1000,
):
    start_date = (
        datetime.strptime(end_date, "%Y-%m-%d")
        - relativedelta(years=2)
    ).strftime("%Y-%m-%d")
    tour_option_time_slot_sales_df = get_tour_option_time_slot_daily_sales(
        start_range_tour_date=start_date,
        end_range_tour_date=end_date,
    )
    tour_daily_sales_df = get_tour_daily_sales(tour_option_time_slot_sales_df)

    df = (
        tour_daily_sales_df
        .filter(F.col("tour_date") < end_date)
        .withColumn('tour_month', F.month(F.to_date("tour_date")))
        .withColumn('tour_year', F.year(F.to_date("tour_date")))
    )

    monthly_df = df.groupby('tour_id', 'tour_year', 'tour_month').agg(F.sum('tickets').alias('tickets'))

    prev_year = target_year - 1

    target_year_col = f"tickets_{target_year}"
    prev_year_col = f"tickets_{prev_year}"

    target_year_df = monthly_df.filter(F.col("tour_year") == target_year).withColumnRenamed("tickets", target_year_col)
    prev_year_df = monthly_df.filter(F.col("tour_year") == prev_year).withColumnRenamed("tickets", prev_year_col)

    yoy_df = (
        target_year_df
        .join(prev_year_df, on=["tour_id", "tour_month"], how="inner")
        .withColumn("yoy_growth", (F.col(target_year_col) - F.col(prev_year_col)) / F.col(prev_year_col))
    )

    summary_df = yoy_df.groupBy("tour_id").agg(
        F.avg("yoy_growth").alias("avg_yoy_growth"),
        (F.sum(F.col("yoy_growth") * F.col(prev_year_col)) / F.sum(prev_year_col)).alias("weighted_yoy_growth"),
        F.sum(target_year_col).alias(target_year_col),
        F.sum(prev_year_col).alias(prev_year_col)
    )

    trending_df = summary_df.filter(
        (F.col("weighted_yoy_growth") >= min_growth) &
        (F.col(prev_year_col) >= min_sales_prev_year)
    ).orderBy(F.col("weighted_yoy_growth").desc())

    return trending_df


def tours_low_zero_share(regular_tours_df, tour_week_sales_df, date_col='date', start_date=None, end_date=None):
    df = tour_week_sales_df.join(regular_tours_df.select('tour_id'), 'tour_id', 'inner')
    print('df rows counts:', df.count())
    print('Input Tours counts:', df.select('tour_id').distinct().count())

    if start_date is not None and end_date is not None:
        print('Filtering date period')
        df = df.filter(
            (F.col(date_col) >= start_date)
            & (F.col(date_col) < end_date)
        )

    tours_df = (
        df
        .groupby('tour_id').agg(
            F.count('*').alias('n'),
            F.sum(F.when(F.col('tickets') == 0, 1).otherwise(0)).alias('n_zero'),
        )
        .withColumn('zero_share', F.round(F.col('n_zero') / F.col('n'), 4))
    )
    tours_low_zero_share_df = tours_df.filter(F.col('zero_share') < 0.1).select('tour_id')
    print('Output Tours counts:', tours_low_zero_share_df.select('tour_id').distinct().count())
    return tours_low_zero_share_df
