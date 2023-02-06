#!/usr/bin/env python
import sys
import re
import argparse
import itertools
import robot.selectionrank.sr_proto_lib.pool_pb2 as pool_pb2
import yt.wrapper as yt
import json
from collections import defaultdict


def parse(l):
    res = l.strip().split("\t")
    assert len(res) >= 2 and len(res) <= 3
    if len(res) == 2:
        res.append(float(1))
    else:
        res[2] = float(res[2])
    return res


def records_generator(inp, plot_rules, out_stats):
    pattern = re.compile(r'(?P<host>.*://[^/]+)(?P<path>/.*)')
    for url, g in itertools.groupby((parse(l) for l in inp), key=lambda x: x[0]):
        m = pattern.match(url)
        if not m:
            continue
        counts = {}
        for k, label, count in g:
            counts[label] = count + counts.get(label, float(0))

        labels = pool_pb2.TLabels()
        for label, count in counts.items():
            labels.Label.append(label)
            labels.Counter.append(count)
            for plot in plot_rules:
                if plot['filter'].search(label) is not None:
                    out_stats[plot['name']] += count

        yield {
            'Host': m.group('host'),
            'Path': m.group('path'),
            'Labels': labels.SerializeToString()
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result', required=True)
    parser.add_argument('--src', required=True)
    parser.add_argument('--plots', required=True)
    parser.add_argument('--proxy')
    parser.add_argument('--token')
    args = parser.parse_args()

    if args.proxy:
        yt.config.set_proxy(args.proxy)
    if args.token:
        yt.config.config['token_path'] = args.token
    if not yt.cypress_commands.exists(args.result):
        yt.cypress_commands.create('table', path=args.result, recursive=True)
    with open(args.plots) as plot_file:
        data = json.load(plot_file)
        plot_rules = []
        for item in data['plots']:
            if 'filter' not in item:
                item['filter'] = item['label']
            plot_rules.append(
                {
                    'name': item['name'],
                    'filter': re.compile(item['filter'])
                }
            )

    res_stats = defaultdict(lambda: 0.0)
    with open(args.src) as inp:
        with yt.Transaction():
            yt.write_table(
                args.result,
                records_generator(inp, plot_rules, res_stats),
                format=yt.YsonFormat(),
            )
            yt.run_sort(
                args.result,
                sort_by=['Host', 'Path'],
            )
            yt.set(yt.ypath_join(args.result, '@sr_plot_statistics'), res_stats)


if __name__ == '__main__':
    sys.exit(main())
