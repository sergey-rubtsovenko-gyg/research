from pydantic import BaseModel
from typing import Union, Dict
import yaml
import os
from demand_forecast.src.env import CONFIGS_DIR
from demand_forecast.src.config.regular_tours import RegularToursConfig
from demand_forecast.src.config.paths import Paths
from demand_forecast.src.daily_demand import get_start_end_dates_for_week_aligned
from rich import print as pprint

class DatasetConfig(BaseModel):
    experiment_name: str
    start_date: str
    end_date: str
    regular_tours: RegularToursConfig
    start_date_weekly_granularity: str = None
    end_date_weekly_granularity: str = None
    paths: Paths
    root_data_path: str = "s3://gygdata/data-products/sdp/rubtsovenko/demand_forecast/experiments"
    experiment_path: str = None
    tour_day_sales_path: str = None
    tour_week_sales_path: str = None
    regular_tours_path: str = None
    trend_tours_path: str = None

    def __init__(self, **data):
        super().__init__(**data)
        self._post_init()

    def _post_init(self):
        self.start_date_weekly_granularity, self.end_date_weekly_granularity = get_start_end_dates_for_week_aligned(
            start_date=self.start_date,
            end_date=self.end_date,
        )
        self._init_paths()

    def _init_paths(self):
        self.experiment_path = os.path.join(self.root_data_path, self.experiment_name)
        self.tour_day_sales_path = os.path.join(self.experiment_path, "tour_day_sales")
        self.tour_week_sales_path = os.path.join(self.experiment_path, "tour_week_sales")
        self.regular_tours_path = os.path.join(self.experiment_path, "regular_tours")
        self.trend_tours_path = os.path.join(self.experiment_path, "trend_tours")

    def print(self):
        pprint(self)


def read_config_from_yaml_file(config_file_path: Union["pathlib.PosixPath", str]) -> Dict:
    with open(config_file_path) as f:
        return yaml.safe_load(f)


def init_config_from_yaml_file(yaml_config_fn) -> 'DatasetConfig':
    config_dict = read_config_from_yaml_file(CONFIGS_DIR / yaml_config_fn)
    # return cls.model_validate(config_dict)
    return DatasetConfig.parse_obj(config_dict)