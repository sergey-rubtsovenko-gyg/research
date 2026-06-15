# from demand_forecast.daily_demand import (
#     get_start_end_dates_for_week_aligned,
#     get_tour_option_time_slot_daily_sales,
#     filter_sales_after_activity_timestamp,
#     get_tour_option_daily_sales,
#     get_tour_daily_sales,
#     get_tour_weekly_sales,
# )
#
#
# def get_tour_day_time_series(start_range_tour_date, end_range_tour_date):
#     tour_option_time_slot_sales_df = get_tour_option_time_slot_daily_sales(
#         start_range_tour_date=start_range_tour_date,
#         end_range_tour_date=end_range_tour_date,
#     )
#
#     tour_daily_sales_df = get_tour_daily_sales(tour_option_time_slot_sales_df)
#
#     return tour_daily_sales_df
#
#
# def get_tour_week_time_series(start_range_tour_date, end_range_tour_date):
#     start_range_tour_date, end_range_tour_date = get_start_end_dates_for_week_aligned(
#         start_date=start_range_tour_date,
#         end_date=end_range_tour_date,
#     )
#
#     tour_option_time_slot_sales_df = get_tour_option_time_slot_daily_sales(
#         start_range_tour_date=start_range_tour_date,
#         end_range_tour_date=end_range_tour_date,
#     )
#
#     tour_week_sales_df = get_tour_weekly_sales(tour_option_time_slot_sales_df)
#
#     return tour_week_sales_df