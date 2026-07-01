import pandas as pd


def get_season(dt):
    month = dt.month
    if month in [12, 1, 2]:   return 0  # winter
    if month in [3, 4, 5]:    return 1  # spring
    if month in [6, 7, 8]:    return 2  # summer
    if month in [9, 10, 11]:  return 3  # autumn


def get_calendar_features(df, date_col='date'):
    df['date'] = pd.to_datetime(df[date_col])
    df['iso_week'] = df['date'].dt.isocalendar().week
    df['iso_year'] = df['date'].dt.isocalendar().year
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['quarter'] = df['date'].dt.quarter
    df['season'] = df['date'].map(get_season)
    return df
