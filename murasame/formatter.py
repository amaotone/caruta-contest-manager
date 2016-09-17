import pandas as pd

from . import CONFIG


def standardize_prefecture(df):
    conf = CONFIG["formatter"]["region"]
    res = df.copy()
    res[conf["ref"]] = res[conf["ref"]].str.replace("[府県]", "")
    res[conf["ref"]] = res[conf["ref"]].str.replace("東京都", "東京")
    return res


def append_region(df):
    conf = CONFIG["formatter"]["region"]
    region = pd.read_excel(conf["file"])
    res = df.merge(region, how="left", on=conf["ref"])
    return res


def select_column(df):
    cols = CONFIG["formatter"]["use"]
    res = df.ix[:, cols]
    return res


def trim_space(df):
    cols = CONFIG["formatter"]["trim"]
    res = df.copy()
    for col in cols:
        # TODO: smart method to find multibyte space
        res[col] = res[col].str.replace("[\s　]", "")
    return res


def formatter(df):
    res = df.copy()
    conf = CONFIG["formatter"]["routine"]
    if conf["trim"]:
        res = trim_space(res)
    if conf["region"]:
        res = append_region(res)
    if conf["use"]:
        res = select_column(res)
    return res
