import yaml

def load_config(file="config.yaml"):
    with open(file, "r") as f:
        conf = yaml.load(f)
    return conf

CONFIG = load_config()