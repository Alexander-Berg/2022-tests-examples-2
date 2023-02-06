#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--geodata',
                        default="geodata.bin",
                        help="path to geodata for checking")
    parser.add_argument('--ipreg',
                        default="-",
                        help="path to test-data with ipreg-ranges; '-' for stdin")
    parser.add_argument('--pairs-check',
                        type=int,
                        default=1,
                        help="how much pairs will be checked in each range (but <= 2^16)")
    parser.add_argument('--debug-progress-step',
                        type=int,
                        default=500000,
                        help="print row-numbers; 0 - disable")
    parser.add_argument('--check-full-reliability',
                        action='store_true',
                        help="try to check all reliabilities instead reg_id only")
    parser.add_argument('--crash-on-error',
                        action='store_true',
                        help="BOOM-mode")
    args = parser.parse_args()
    return args


def get_corrected_pairs_value(value):
    max_value = 2 ** 16
    value = max(value, 1)
    return min(max_value, value)


def make_reliabilites_hash(traits_json):
    import json
    parsed_traits = json.loads(traits_json)

    traits_keys = parsed_traits.keys()
    traits = []

    if 'is_yandex_staff' in traits_keys:
        traits.append({'reliability': 0, 'region_id': 9999})

    if 'region_id' in traits_keys and 'reliability' in traits_keys:
        traits.append({'reliability': int(parsed_traits['reliability']), 'region_id': int(parsed_traits['region_id'])})

    return traits


class Checker(object):
    def __init__(self, args):
        import geobase5
        self.lookup = geobase5.Lookup(args.geodata)

        self.in_stream = sys.stdin if args.ipreg == "-" else open(args.ipreg)
        self.pairs_to_check = get_corrected_pairs_value(args.pairs_check)
        self.debug_progress_step = args.debug_progress_step
        self.crash_mode = args.crash_on_error

        self.check_full_reliability = args.check_full_reliability
        self.checker_fn = self.lookup.reliabilities_by_ip if self.check_full_reliability else self.lookup.region_id

        self.bad_lines = 0

    BAD_ID = -5
    SPEC_NETS_ID = 99999
    YANDEX_REG_ID = 9999
    ROOT_ID = 0

    def make_check(self):
        rows_total = 0
        for line in self.in_stream:
            rows_total += 1
            if self.debug_progress_step and (0 == rows_total % self.debug_progress_step):
                print >>sys.stderr, "%d..." % rows_total
            self.check_range(line.strip())

        print >>sys.stderr, "STATS: %d/%d (total/bad)" % (rows_total, self.bad_lines)

    def check_range(self, line):
        if not line or line.startswith('#'):
            return

        addr_lo, addr_hi, traits_json = line.replace('-', ' ').replace('\t', ' ').split()

        import ipaddr
        addr_from = ipaddr.IPAddress(addr_lo)
        addr_to = ipaddr.IPAddress(addr_hi)
        range_rels = make_reliabilites_hash(traits_json)

        if 0 == len(range_rels):
            self.bad_lines += 1
            self.err(">>> strange rels-data: %s" % line)
            return

        region_id = int(range_rels[0]["region_id"])
        wanted_answer = range_rels if self.check_full_reliability else region_id

        total_amount = 0
        checked_amount = 0

        while (total_amount < self.pairs_to_check * 2) and (addr_from <= addr_to):
            total_amount += 2
            checked_amount += self.check_addr(addr_from, wanted_answer) + self.check_addr(addr_to, wanted_answer)

            addr_from += 1
            addr_to -= 1

        if checked_amount != total_amount:
            self.bad_lines += 1
            msg = "non-consistent results were detected!\n%s\n>> result: %d/%d" % (line, checked_amount, total_amount)
            self.err(msg)

    def check_addr(self, addr, wanted_data):
        result = 0
        got_data = None
        err_msg = ""

        try:
            got_data = self.checker_fn(str(addr))
            if wanted_data == got_data:
                result = 1
        except Exception as ex:
            err_msg = str(ex)

        if 0 == result:
            self.err("%s [%s] => %s != %s (wanted)" % (err_msg, addr, got_data, wanted_data))
        return result

    def err(self, msg):
        msg = "FAIL: %s" % msg
        if self.crash_mode:
            raise Exception(msg)
        else:
            print >>sys.stderr, msg


def main(args):
    try:
        checker = Checker(args)

        print >>sys.stderr, "checking ipreg from [", args.ipreg, "]..."
        checker.make_check()
    except Exception as ex:
        print >>sys.stderr, ">>> FAIL: %s" % ex
        return 1

    print >>sys.stderr, "complete"
    return 0


if __name__ == "__main__":
    sys.exit(main(parse_args()))
