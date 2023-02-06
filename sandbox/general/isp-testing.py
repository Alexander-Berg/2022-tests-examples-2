#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--geodata',
                        default="geodata.bin",
                        help="path to geodata for checking")
    parser.add_argument('--isp-data',
                        default="-",
                        help="path to test-data with isp-ranges; '-' for stdin")
    parser.add_argument('--pairs-check',
                        type=int,
                        default=1,
                        help="how much pairs will be checked in each range (but <= 2^16)")
    parser.add_argument('--debug-progress-step',
                        type=int,
                        default=5000,
                        help="print row-numbers; 0 - disable")
    parser.add_argument('--crash-on-error',
                        action='store_true',
                        help="BOOM-mode")
    args = parser.parse_args()
    return args


def get_corrected_pairs_value(value):
    max_value = 2 ** 16
    value = max(value, 1)
    return min(max_value, value)


class Checker(object):
    def __init__(self, args):
        import geobase6
        self.lookup = geobase6.Lookup(args.geodata)

        self.in_stream = sys.stdin if args.isp_data == "-" else open(args.isp_data)
        self.pairs_to_check = get_corrected_pairs_value(args.pairs_check)
        self.debug_progress_step = args.debug_progress_step
        self.crash_mode = args.crash_on_error

        self.bad_lines = 0

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

        TUN6TO4 = "2002:"
        if line.startswith(TUN6TO4):
            print >>sys.stderr, "NB: skip 6to4-addr", line
            return

        addr_lo, addr_hi, isp_code = line.replace('-', ' ').replace('\t', ' ').split()

        addr_from = addr_lo
        addr_to = addr_hi
        isp_code = int(isp_code)

        total_amount = 2
        checked_amount = self.check_addr(addr_from, isp_code) + self.check_addr(addr_to, isp_code)

        if checked_amount != total_amount:
            self.bad_lines += 1
            msg = "non-consistent results were detected!\n%s\n>> result: %d/%d" % (line, checked_amount, total_amount)
            self.err(msg)

    def check_addr(self, addr, wanted_isp):
        result = 0
        got_isp = None
        err_msg = ""

        try:
            got_isp = self.lookup.get_isp_code_by_ip(addr)
            if wanted_isp == got_isp:
                result = 1
        except Exception as ex:
            err_msg = str(ex)

        if 0 == result:
            self.err("%s [%s] => %s != %s (wanted)" % (err_msg, addr, got_isp, wanted_isp))
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

        print >>sys.stderr, "checking isp from [", args.isp_data, "]..."
        checker.make_check()
    except Exception as ex:
        print >>sys.stderr, ">>> FAIL: %s" % ex
        return 1

    print >>sys.stderr, "complete"
    return 0


if __name__ == "__main__":
    sys.exit(main(parse_args()))
