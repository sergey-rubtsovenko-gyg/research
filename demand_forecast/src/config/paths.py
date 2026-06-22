from pydantic import BaseModel
from typing import List
import os
import pandas as pd


class Paths(BaseModel):
    root: str = "s3://gygdata/data-products/sdp/rubtsovenko/demand_forecast/experiments"
    experiment: str = None
    tour_day_sales: str = None
    tour_week_sales: str = None
    regular_tours: str = None
    trend_tours: str = None
    analytics_baseline: str = None
