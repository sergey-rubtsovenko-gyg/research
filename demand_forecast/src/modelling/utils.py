import pandas as pd


def get_feature_list(continious_features, categorical_features):
    intersection = list(set(continious_features) & set(categorical_features))
    if len(intersection) > 0:
        raise ValueError(f'There are features present in both conitions_features and categorica_features: {intersection}')
    return continious_features + categorical_features


def get_train_test_periods(test_start_date, train_weeks, test_weeks):
    train_start_date = (pd.Timestamp(test_start_date) - pd.Timedelta(weeks=train_weeks)).strftime('%Y-%m-%d')
    train_end_date = test_start_date
    test_end_date = (pd.Timestamp(test_start_date) + pd.Timedelta(weeks=test_weeks)).strftime('%Y-%m-%d')
    return train_start_date, train_end_date, test_start_date, test_end_date
