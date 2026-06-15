from pydantic import BaseModel
from typing import List
import os
import pandas as pd


class RegularToursConfig(BaseModel):
    end_date: str
    n_years: int = 3
    n_months_buffer: int = 6
    avg_tickets_per_day: int = 10
    days_with_sales_share: float = 0.0
