from pydantic import BaseModel
from typing import Union, Dict
import yaml
import os
from demand_forecast.src.env import CONFIGS_DIR
from demand_forecast.src.config.regular_tours import RegularToursConfig
from demand_forecast.src.config.paths import Paths
from demand_forecast.src.daily_demand import get_start_end_dates_for_week_aligned
from rich import print as pprint
from pydantic import BaseModel, Field

class DatasetConfig(BaseModel):
    experiment_name: str
    start_date: str
    end_date: str
    regular_tours: RegularToursConfig
    start_date_weekly_granularity: str = None
    end_date_weekly_granularity: str = None
    paths: Paths = Field(default_factory=Paths)

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
        self.paths.experiment = os.path.join(self.paths.root, self.experiment_name)
        self.paths.tour_day_sales = os.path.join(self.paths.experiment, "tour_day_sales")
        self.paths.tour_week_sales = os.path.join(self.paths.experiment, "tour_week_sales")
        self.paths.regular_tours = os.path.join(self.paths.experiment, "regular_tours")
        self.paths.trend_tours = os.path.join(self.paths.experiment, "trend_tours")
        self.paths.analytics_baseline = os.path.join(self.paths.experiment, "analytics_baseline")

    def print(self):
        pprint(self)


def read_config_from_yaml_file(config_file_path: Union["pathlib.PosixPath", str]) -> Dict:
    with open(config_file_path) as f:
        return yaml.safe_load(f)


def init_config_from_yaml_file(yaml_config_fn) -> 'DatasetConfig':
    config_dict = read_config_from_yaml_file(CONFIGS_DIR / yaml_config_fn)
    # return cls.model_validate(config_dict)
    return DatasetConfig.parse_obj(config_dict)
