from demand_forecast.src.env import ROOT_DIR, CONFIGS_DIR
from demand_forecast.src.config.main import DatasetConfig, read_config_from_yaml_file, init_config_from_yaml_file
import argparse
import os
from demand_forecast.src.env import ROOT_DIR, CONFIGS_DIR, EXPERIMENTS_DIR
import subprocess


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download data from s3")
    parser.add_argument("--config", required=True, help="Input config file")
    return parser.parse_args()


def main(config_fn) -> None:
    config = init_config_from_yaml_file(config_fn)

    s3_experiment_data_path = config.paths.experiment
    local_experiment_data_path = os.path.join(EXPERIMENTS_DIR, config.experiment_name)

    config.print()

    subprocess.run(
        [
            "aws", "s3", "cp", "--recursive",
            s3_experiment_data_path,
            local_experiment_data_path,
        ],
        check=True
    )


if __name__ == "__main__":
    args = parse_args()
    main(config_fn=args.config)
