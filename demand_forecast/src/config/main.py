from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Union, Dict
import yaml
import os
from demand_forecast.src.env import CONFIGS_DIR
from demand_forecast.src.config.paths import Paths, DataCollection, Preprocessing, Modelling
from demand_forecast.src.data_collection.tour_sales import get_start_end_dates_for_week_aligned
from rich import print as pprint


class DatasetConfig(BaseModel):
    experiment_name: str
    start_date: str
    end_date: str
    start_date_weekly_granularity: str = None
    end_date_weekly_granularity: str = None
    root_path: str = "s3://gygdata/data-products/sdp/rubtsovenko/demand_forecast/experiments"
    experiment_path: str = None
    data_collection: DataCollection = Field(default_factory=DataCollection)
    preprocessing: Preprocessing = Field(default_factory=Preprocessing)
    modelling: Modelling = Field(default_factory=Modelling)

    def __init__(self, **data):
        super().__init__(**data)
        self._init()

    def _init(self):
        self.start_date_weekly_granularity, self.end_date_weekly_granularity = get_start_end_dates_for_week_aligned(
            start_date=self.start_date,
            end_date=self.end_date,
        )
        self.experiment_path = os.path.join(self.root_path, self.experiment_name)
        self.data_collection.path = os.path.join(self.experiment_path, 'data_collection')
        self.data_collection.tour_day_sales_path = os.path.join(self.data_collection.path, 'tour_day_sales')
        self.data_collection.tour_week_sales_path = os.path.join(self.data_collection.path, 'tour_week_sales')

        self.preprocessing.path = os.path.join(self.experiment_path, 'preprocessing')
        self.preprocessing.tour_day_sales_path = os.path.join(self.preprocessing.path, 'tour_day_sales')
        self.preprocessing.tour_week_sales_path = os.path.join(self.preprocessing.path, 'tour_week_sales')
        self.preprocessing.tour_week_inference_path = os.path.join(self.preprocessing.path, 'tour_week_inference')


        self.modelling.path = os.path.join(self.experiment_path, 'modelling')
        self.modelling.tour_week_analytics_baseline_path = os.path.join(self.modelling.path, 'tour_week_analytics_baseline')

    def print(self):
        pprint(self)


def read_config_from_yaml_file(config_file_path: Union["pathlib.PosixPath", str]) -> Dict:
    with open(config_file_path) as f:
        return yaml.safe_load(f)


def init_config_from_yaml_file(yaml_config_fn) -> 'DatasetConfig':
    config_dict = read_config_from_yaml_file(CONFIGS_DIR / yaml_config_fn)
    # return cls.model_validate(config_dict)
    return DatasetConfig.parse_obj(config_dict)
