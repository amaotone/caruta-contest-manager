import pandas as pd


class Formatter(object):
    def __init__(self, df):
        self.data = df

    def trim_space(self, cols):
        for col in cols:
            self.data[col] = self.data[col].str.replace("[\s　]", "")

    def standardize_prefecture(self, col):
        self.data[col] = self.data[col].str.replace("[府県]", "")
        self.data[col] = self.data[col].str.replace("東京都", "東京")

    def append_region(self, pref_col, region_file):
        region = pd.read_excel(region_file)
        self.data = self.data.merge(region, how="left", on=pref_col)

    def select_column(self, cols):
        self.data = self.data.ix[:, cols]


def formatter(df):
    from . import CONFIG
    conf = CONFIG["formatter"]
    routine = CONFIG["formatter"]["routine"]

    fmt = Formatter(df)
    if routine["trim"]:
        fmt.trim_space(conf["trim"])
    if routine["region"]:
        base = conf["region"]["base"]
        file = conf["region"]["file"]
        fmt.standardize_prefecture(base)
        fmt.append_region(base, file)
    if routine["select"]:
        fmt.select_column(conf["select"])

    return fmt.data
