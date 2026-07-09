from pydantic import BaseModel
from typing import List
import os
import pandas as pd


class Paths(BaseModel):
    root: str = "s3://gygdata/data-products/sdp/rubtsovenko/demand_forecast/experiments"
    experiment: str = None

class DataCollection(BaseModel):
    path: str = None
    tour_day_sales_path: str = None
    tour_week_sales_path: str = None


class Preprocessing(BaseModel):
    path: str = None
    tour_day_sales_path: str = None
    tour_week_sales_path: str = None
    tour_week_inference_path: str = None


class Modelling(BaseModel):
    path: str = None
    tour_week_analytics_baseline_path: str = None
    tour_week_lightgbm_sales_path: str = None