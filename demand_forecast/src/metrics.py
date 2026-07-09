import pandas as pd
import numpy as np

def get_wape(actual, forecast, precision=2):
    return np.round(sum(abs(forecast - actual)) / sum(actual), precision)

def get_bias(actual, forecast, precision=2):
    return np.round(sum(np.array(forecast) - np.array(actual)) / sum(np.array(actual)), precision)


def discard_nulls(df, actual_col, forecast_col):
    actual_null_cnt = sum(df[actual_col].isnull())
    forecast_null_cnt = sum(df[forecast_col].isnull())

    if actual_null_cnt > 0:
        full_rows_cnt = len(df)
        print('Full df count:', len(df))
        print(f'Actuals null count: {actual_null_cnt} (share={np.round(actual_null_cnt / full_rows_cnt, 2)})')
        df = df[~df[actual_col].isnull()].reset_index(drop=True)
        print('Dropped rows with null actual value')

    if forecast_null_cnt > 0:
        full_rows_cnt = len(df)
        print('Full df count:', len(df))
        print(f'Forecast null count: {forecast_null_cnt} (share={np.round(forecast_null_cnt / full_rows_cnt, 2)})')
        df = df[~df[forecast_col].isnull()].reset_index(drop=True)
        print('Dropped rows with null forecast value')

    return df


def get_micro_metrics(df, actual_col, forecast_col):
    df = discard_nulls(df, actual_col, forecast_col)
    wape_score = get_wape(df[actual_col], df[forecast_col])
    bias_score = get_bias(df[actual_col], df[forecast_col])
    print(f'WAPE (micro): {wape_score}')
    print(f'bias (micro): {bias_score}')


def get_macro_metrics(df, actual_col, forecast_col):
    df = discard_nulls(df, actual_col, forecast_col)
    metrics_per_tour = (
        df.groupby('tour_id', observed=True).apply(lambda g: pd.Series({
            'wape': get_wape(g[actual_col], g[forecast_col]),
            'bias': get_bias(g[actual_col], g[forecast_col]),
        }), include_groups=False)
        .reset_index()
    )
    print(f"WAPE (macro): {metrics_per_tour['wape'].mean()}")
    print(f"bias (macro): {metrics_per_tour['bias'].mean()}")
