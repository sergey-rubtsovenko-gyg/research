from pydantic import BaseModel
from typing import List
import os
import pandas as pd


class Paths(BaseModel):
    root_data_path: str = "s3://gygdata/data-products/sdp/rubtsovenko/demand_forecast/experiments"
    experiment_path: str = None
    tour_day_sales_path: str = None
    tour_week_sales_path: str = None
    regular_tours_path: str = None
    trend_tours_path: str = None
