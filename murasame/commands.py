import glob
import os

import pandas as pd

from .divider import Divider
from .formatter import Formatter
from .maker import Maker
from .utils import load_setting

tmpdir = load_setting()['system']['tmpdir']
resdir = load_setting()['system']['resdir']


def formatter():
    setting = load_setting()['formatter']

    dfs = pd.read_excel(setting['input'], sheetname=None)
    df = pd.concat(list(dfs.values()))

    fmt = Formatter(df)
    fmt.trim_space()
    if setting['region']['use']:
        base = setting['region']['base']
        file = setting['region']['file']
        fmt.trim_prefecture(base)
        fmt.append_region(base, file)
    fmt.select_column(setting['columns'])
    fmt.save(os.path.join(tmpdir, 'formatter'))


def divider():
    setting = load_setting()['divider']
    df = pd.read_excel(os.path.join(tmpdir, 'formatter', 'sheet.xlsx'))
    div = Divider(df, files=setting["files"], base=setting["base"])
    div.save(os.path.join(tmpdir, 'divider'))


def maker():
    setting = load_setting()['maker']

    files = glob.glob(os.path.join(tmpdir, 'divider', '*.xlsx'))
    for f in files:
        root, base = os.path.split(f)
        name, ext = os.path.splitext(base)

        maker = Maker(file=f)
        maker.make_board(keys=setting['board']['keys'])
        maker.make_sheet(id_label=setting['sheet']['id'], seat_label='座席',
                         fill='不戦')

        boardname = '{}_board.xlsx'.format(name)
        sheetname = '{}_sheet.xlsx'.format(name)
        maker.save_board(os.path.join(resdir, boardname))
        maker.save_sheet(os.path.join(resdir, sheetname),
                         sort_by=setting['sheet']['sort_by'])

if __name__ == '__main__':
    formatter()
    divider()
    maker()