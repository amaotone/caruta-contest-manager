import os

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
    cols = CONFIG["formatter"]["select"]
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
        res = standardize_prefecture(res)
        res = append_region(res)
    if conf["select"]:
        res = select_column(res)
    return res


def divider(df):
    conf = CONFIG["divider"]
    out = conf["out"]
    os.makedirs(out, exist_ok=True)

    files = conf["files"]
    writers = {}
    for filename in files.keys():
        path = os.path.join(out, "{}.xlsx".format(filename))
        writers[filename] = pd.ExcelWriter(path)

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
