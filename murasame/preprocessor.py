import os

import pandas as pd

from . import CONFIG

conf = CONFIG["formatter"]


class Formatter(object):
    def __init__(self, df):
        self.data = df

    def trim_space(self):
        cols = conf["trim"]
        for col in cols:
            self.data[col] = self.data[col].str.replace("[\s　]", "")

    def standardize_prefecture(self):
        ref = conf["region"]["ref"]
        self.data[ref] = self.data[ref].str.replace("[府県]", "")
        self.data[ref] = self.data[ref].str.replace("東京都", "東京")

    def append_region(self):
        file = conf["region"]["file"]
        ref = conf["region"]["ref"]
        region = pd.read_excel(file)
        self.data = self.data.merge(region, how="left", on=ref)

    def select_column(self):
        cols = conf["select"]
        self.data = self.data.ix[:, cols]

    def __call__(self):
        routine = conf["routine"]
        if routine["trim"]:
            self.trim_space()
        if routine["region"]:
            self.standardize_prefecture()
            self.append_region()
        if routine["select"]:
            self.select_column()
        return self.data


def formatter(df):
    fmt = Formatter(df)
    return fmt()


def divider(df):
    conf = CONFIG["divider"]
    out = conf["out"]
    os.makedirs(out, exist_ok=True)

    # make xlsxwriter
    files = conf["files"]
    writers = {}
    for filename in files.keys():
        path = os.path.join(out, "{}.xlsx".format(filename))
        writers[filename] = pd.ExcelWriter(path)

    # divide groups among xlsxwriters
    for group, member in df.groupby(conf["ref"]):
        member = member.drop(conf["ref"], axis=1)
        for filename, groups in files.items():
            if group in groups:
                target = writers[filename]
                break
        else:
            raise RuntimeError
        member.to_excel(target, group, index=False)

    for w in writers.values():
        w.save()
