import pandas as pd


def has_weekly_timeseries_gaps(date_series):
    dates = date_series.sort_values()
    return (dates.diff().dropna() != pd.Timedelta(weeks=1)).any()


def fill_gaps(df, end_date):
    df['is_inputed'] = False
    df_without_gaps = (
        df
        .groupby('tour_id', group_keys=False).apply(
            lambda x: fill_gaps_one_timeseries(x, end_date=end_date)
        )
    )
    return df_without_gaps


def fill_gaps_one_timeseries(timeseries, end_date, freq='W-MON'):
    full_range = pd.date_range(
        start=timeseries['date'].min(),
        end=end_date,
        freq=freq  # weekly, starting Monday — adjust to your week start
    )
    return (
        timeseries.set_index('date')
        .reindex(full_range)
        .assign(tour_id=timeseries['tour_id'].iloc[0])
        .fillna({'tickets': 0, 'is_inputed': True})
        .reset_index()
        .rename(columns={'index': 'date'})
    )
