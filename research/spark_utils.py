from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.types import StringType
from pyspark.sql import Window
import numpy as np


def print_cnt_share(count, reference_count, prefix='Tours count', share_message='', round_precision=2):
    share_prc = np.round( (count / reference_count) * 100, round_precision)
    if share_message:
        print(f"{prefix}: {count} ({share_prc}% {share_message})")
    else:
        print(f"{prefix}: {count} ({share_prc}%)")


def check_tour_duplicates(df):
    rows_cnt = df.count()
    tours_cnt = df.select("tour_id").distinct().count()

    print(f"All rows count: {rows_cnt}")
    print(f"Distinct tours count: {tours_cnt}")
    print(f"Table Has tour Duplicates: {rows_cnt != tours_cnt}")


def groupby_count(df, cols: list, sort_ascending=False):
    return df.groupBy(cols).count().orderBy("count", ascending=sort_ascending)


def groupby_count_share(df, cols: list, share_round_precision=2, sort_ascending=False):
    total = df.count()
    agg_df = (
        df.groupBy(cols)
        .count()
        .withColumn("share%", F.round( (F.col("count") / total) * 100, share_round_precision))
        .orderBy("count", ascending=sort_ascending)
    )
    return agg_df


def groupby_sum_share(df, agg_cols: list, sum_col: str, share_round_precision=2, sort_ascending=False):
    total = float(df.select(F.sum(sum_col)).collect()[0][0])
    agg_df = (
        df.groupBy(agg_cols)
        .agg(F.sum(sum_col).alias(sum_col))
        .withColumn("share%", F.round( (F.col(sum_col) / total) * 100, share_round_precision))
        .orderBy(sum_col, ascending=sort_ascending)
    )
    return agg_df


def tours_count_per_group_with_activation_flag(tour_df):
    cols = ['location_id', 'location_name', 'category_lvl1', 'category_lvl2']
    tours_count_per_group_df = (
        tour_df.groupby(cols).agg(F.count('*').alias('group_tours_cnt'))
        .sort(cols)
    )

    cols=['location_id', 'location_name', 'category_lvl1', 'category_lvl2', 'is_activated']
    tours_count_per_group_and_activation_flag_df = (
        tour_df.groupby(cols).agg(F.count('*').alias('subgroup_tours_cnt'))
        .sort(cols)
    )

    tours_count_per_group_and_activation_flag_df = (
        tours_count_per_group_and_activation_flag_df
        .join(
            tours_count_per_group_df,
            ['location_id', 'location_name', 'category_lvl1', 'category_lvl2'],
            'inner',
        )
        .sort(cols)
        .withColumn('subgroup_share%', F.round(F.col('subgroup_tours_cnt') / F.col('group_tours_cnt') * 100, 2))
    )
    return tours_count_per_group_and_activation_flag_df