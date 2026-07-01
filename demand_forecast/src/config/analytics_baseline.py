from pydantic import BaseModel
from typing import List
import os
import pandas as pd


class AnalyticsBaselineConfig(BaseModel):
    start_date: str
    end_date: str
