import re
import yaml
from yaml.loader import SafeLoader
import subprocess

with open("./conf/base/parameters.yml") as f:
    datasets = yaml.load(f, Loader=SafeLoader)["datasets"]

for dataset in datasets:
    start_date = re.findall("(\d+)", dataset)[0]
    subprocess.run(
        f"kedro run --pipeline {start_date}_execution", shell=True, check=True
    )
