#!/usr/bin/env python
# coding=utf-8

import collections
import itertools
import numpy as np
import os
import sys
import unittest


# Fields in show log which refer to money
MONEY_FIELDS = (
    'click_price',
    'bid',
    'price',
    'fee',
    'min_fee',
    'vendor_click_price',
    'ctr',
    'min_bid',
)


def parse_tskv_line(line):
    """
    Parse log lines which look like that:
        bs_block_id=    position=1      uuid=   show_block_id=7775114509902308825       mn_ctr=0.191292 best_deal=0     vbid=0  vendor_click_price=0
    """
    return dict(
        itertools.imap(
            lambda s: s.split('=', 1),
            itertools.ifilter(  # get rid of empty lines
                lambda x: x,
                itertools.islice(  # skip 'tskv' heading element
                    line.strip().split('\t'),
                    1, None
                )
            )
        )
    )


def extract_metrics(rec):
    """
    Extract money metrics from market report show log record
    :param rec: dict with records values (values expected to be strings)
    """
    res = {}
    for field_name in MONEY_FIELDS:
        res[field_name] = float(rec.get(field_name, '0.0'))
    return res


def calc_money_metrics_from_show_log(f):
    """
    Calculate money metrics from market-report show log (log must be in TSKV format)
    :param f: file-like object to read log lines from
    """
    sums = extract_metrics({})
    values = collections.defaultdict(list)
    count = 0
    for line in f:
        rec = parse_tskv_line(line)
        if rec.get('pp') == '18':
            continue
        d = extract_metrics(rec)
        for key, val in d.iteritems():
            sums[key] += val
            values[key].append(val)
        count += 1
    res = {}
    for key, val in sums.iteritems():
        res[key] = {
            'sum': val,
            'avg': val / count if count != 0 else 0.0,
            'median': float(np.median(values[key])) if values[key] else 0.0,
        }
    return count, res


class T(unittest.TestCase):
    def test_parce_tskv_line(self):
        self.assertEqual(parse_tskv_line(''), {})
        self.assertEqual(parse_tskv_line('\t'), {})
        self.assertEqual(parse_tskv_line('\n'), {})
        d = parse_tskv_line('tskv\ta=b\tc=d\t')
        self.assertEqual(len(d), 2)
        self.assertEqual(d['a'], 'b')
        self.assertEqual(d['c'], 'd')

    def test_extract_metrics(self):
        extract_metrics({})
        d = extract_metrics({'bid': '1234'})
        self.assertEqual(d['bid'], 1234.0)

    def test_calc_money_metrics_from_show_log_on_empty_file(self):
        import StringIO
        f = StringIO.StringIO()
        count, stats = calc_money_metrics_from_show_log(f)
        self.assertEqual(count, 0)
        self.assertEqual(stats['click_price']['avg'], 0.0)

    def test_calc_money_metrics_from_show_log(self):
        import StringIO
        f = StringIO.StringIO()
        f.write('tskv\tclick_price=14\tbid=100\tprice=4500\n')
        f.write('tskv\tclick_price=55\tbid=200\tprice=45000\n')
        f.write('tskv\tclick_price=37\tbid=700\tprice=12500\n')
        f.write('tskv\tclick_price=20\tbid=200\tprice=15500\n')
        f.write('tskv\tclick_price=20\tbid=200\tprice=15500\tpp=18\n')
        f.seek(0)
        count, stats = calc_money_metrics_from_show_log(f)
        self.assertEqual(stats['click_price']['avg'], 31.5)
        self.assertEqual(stats['bid']['avg'], 300.0)
        self.assertEqual(stats['bid']['avg'], 300.0)
        self.assertEqual(stats['price']['avg'], 19375.0)
        self.assertEqual(stats['price']['median'], 14000.0)


def main():
    with open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin as f:
        print calc_money_metrics_from_show_log(f)


if __name__ == '__main__':
    if os.environ.get('UNITTEST') == '1':
        unittest.main()
    else:
        main()
