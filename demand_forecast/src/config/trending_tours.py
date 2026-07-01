from pydantic import BaseModel
from typing import List
import os
import pandas as pd


class TrendToursConfig(BaseModel):
    end_date: str
    target_year: int
    min_growth: float = 0.3
    min_sales_prev_year: int = 1000
