import pandas as pd

from . import load_setting


class Formatter(object):
    def __init__(self, df):
        self.data = df

    def trim_space(self):
        for col, type_ in self.data.dtypes.iteritems():
            if type_ == "object":
                self.data[col] = self.data[col].str.replace("[\s　]", "")

    def trim_prefecture(self, col):
        self.data[col] = self.data[col].str.replace("[府県]", "")
        self.data[col] = self.data[col].str.replace("東京都", "東京")

    def append_region(self, pref_col, region_file):
        region = pd.read_excel(region_file)
        self.data = self.data.merge(region, how="left", on=pref_col)

    def select_column(self, cols):
        self.data = self.data.ix[:, cols]


def formatter(df):
    setting = load_setting()['formatter']
    fmt = Formatter(df)

    fmt.trim_space()

    if setting['region']['use']:
        base = setting['region']['base']
        file = setting['region']['file']
        fmt.trim_prefecture(base)
        fmt.append_region(base, file)

    fmt.select_column(setting['column'])

    return fmt.data
