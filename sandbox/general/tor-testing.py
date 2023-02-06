#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--geodata',
                        default="geodata.bin",
                        help="path to geodata for checking")
    parser.add_argument('--tor-data',
                        default="-",
                        help="path to test-data with TOR ip-addresses; '-' for stdin")
    parser.add_argument('--debug-progress-step',
                        type=int,
                        default=100,
                        help="print row-numbers; 0 - disable")
    parser.add_argument('--crash-on-error',
                        action='store_true',
                        help="BOOM-mode")
    args = parser.parse_args()
    return args


class Checker(object):
    def __init__(self, args):
        import geobase5
        self.lookup = geobase5.Lookup(args.geodata)

        self.in_stream = sys.stdin if args.tor_data == "-" else open(args.tor_data)
        self.debug_progress_step = args.debug_progress_step
        self.crash_mode = args.crash_on_error

    def make_check(self):
        rows_total = 0
        founded = 0

        for line in self.in_stream:
            rows_total += 1
            if self.debug_progress_step and (0 == rows_total % self.debug_progress_step):
                print >>sys.stderr, "%d..." % rows_total

            founded += self.check_addr(line.strip())

        print >>sys.stderr, "STATS: %d/%d (total/bad)" % (rows_total, founded)
        if rows_total != founded:
            self.err("FAIL")

    def check_addr(self, addr):
        try:
            found = self.lookup.is_tor(addr)
            if found:
                return 1
            else:
                self.err("TOR exit-node not found: %s" % addr)
        except Exception as ex:
            self.err("%s!!!\nUnable to make TOR check for IP %s" % (ex, addr))

        return 0

    def err(self, msg):
        msg = "FAIL: %s" % msg
        if self.crash_mode:
            raise Exception(msg)
        else:
            print >>sys.stderr, msg


def main(args):
    try:
        checker = Checker(args)

        print >>sys.stderr, "checking TOR from [", args.tor_data, "]..."
        checker.make_check()
        print >>sys.stderr, "complete."
    except Exception as ex:
        print >>sys.stderr, ">>> FAIL: %s" % ex
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(parse_args()))
