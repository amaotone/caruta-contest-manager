import yaml

def load_setting(file="setting.yml"):
    with open(file, "r") as f:
        setting = yaml.load(f)
    return setting
