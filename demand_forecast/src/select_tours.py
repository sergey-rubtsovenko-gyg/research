from dateutil.relativedelta import relativedelta
from datetime import datetime
import textwrap

from demand_forecast.src.daily_demand import (
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
    print(f"Time Range: [{start_date}, {end_date})")

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