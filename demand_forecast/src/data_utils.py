def save_df_to_s3(df, s3_path, save_one_file=True, overwrite=False):
    if save_one_file:
        df = df.coalesce(1)
    writer = df.write
    if overwrite:
        writer = writer.mode('overwrite')
    writer.parquet(s3_path)
