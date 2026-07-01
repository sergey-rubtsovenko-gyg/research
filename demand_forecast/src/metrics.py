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


def get_metrics(df, actual_col, forecast_col):
    df = discard_nulls(df, actual_col, forecast_col)
    wape_score = get_wape(df[actual_col], df[forecast_col])
    bias_score = get_bias(df[actual_col], df[forecast_col])
    print(f'WAPE: {wape_score}')
    print(f'bias: {bias_score}')
