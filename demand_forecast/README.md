Copy data locally

```
aws_login_dwh

venv_activate
python
```

```
from demand_forecast.src.env import ROOT_DIR, CONFIGS_DIR
from demand_forecast.src.config.main import DatasetConfig, read_config_from_yaml_file, init_config_from_yaml_file

import subprocess

subprocess.run(
    [
        "aws", "s3", "cp",
        "s3://gygdata/data-products/sdp/rubtsovenko/demand_forecast/experiments/experiment_1/trend_tours",
        "./data/trend_tours",
        "--recursive"
    ],
    check=True
)
```