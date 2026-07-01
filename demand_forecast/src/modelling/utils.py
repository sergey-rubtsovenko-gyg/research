def get_feature_list(continious_features, categorical_features):
    intersection = list(set(continious_features) & set(categorical_features))
    if len(intersection) > 0:
        raise ValueError(f'There are features present in both conitions_features and categorica_features: {intersection}')
    return continious_features + categorical_features
