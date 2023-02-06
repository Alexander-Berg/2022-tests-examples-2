#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--geodata',
                        default="geodata.bin",
                        help="path to geodata for checking")
    parser.add_argument('--assets',
                        default="-",
                        help="path to test-data with AS-data; '-' for stdin")
    parser.add_argument('--pairs-check',
                        type=int,
                        default=1,
                        help="how much pairs will be checked in each range (but <= 2^16)")
    parser.add_argument('--debug-progress-step',
                        type=int,
                        default=10000,
                        help="print row-numbers; 0 - disable")
    parser.add_argument('--check-full-range',
                        action='store_true',
                        help="check full AS-range (available in VERSION >= 5.0.0)")
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
        import geobase5
        self.lookup = geobase5.Lookup(args.geodata)

        self.assets_stream = sys.stdin if args.assets == "-" else open(args.assets)
        self.pairs_to_check = get_corrected_pairs_value(args.pairs_check)
        self.debug_progress_step = args.debug_progress_step
        self.check_full_range = args.check_full_range
        self.crash_mode = args.crash_on_error

        self.bad_lines = 0

    def make_check(self):
        rows_total = 0
        for line in self.assets_stream:
            rows_total += 1
            if self.debug_progress_step and (0 == rows_total % self.debug_progress_step):
                print >>sys.stderr, "%d..." % rows_total
            self.check_net(line.strip())

        print >>sys.stderr, "STATS: %d/%d (total/bad)" % (rows_total, self.bad_lines)

    def check_net(self, line):
        net_parts = line.replace('-', ' ').replace('\t', ' ').split()
        if 3 > len(net_parts):
            self.err("bad row: " + line)
            return

        addr_begin = net_parts[0]
        addr_end = net_parts[1]
        as_names = net_parts[2:]

        if self.check_full_range and not self.check_range(addr_begin, addr_end, as_names):
            self.err("problems with [%s]" % (line))

        import ipaddr
        addr_from = ipaddr.IPAddress(addr_begin)
        addr_to = ipaddr.IPAddress(addr_end)

        total_amount = 0
        checked_amount = 0

        while (total_amount < self.pairs_to_check * 2) and (addr_from < addr_to):
            total_amount += 2
            checked_amount += self.check_addr(addr_from, as_names) + self.check_addr(addr_to, as_names)

            addr_from += 1
            addr_to -= 1

        if checked_amount != total_amount:
            self.bad_lines += 1
            self.err("non-consistent results were detected!\n>> result: %d/%d" % (checked_amount, total_amount))

    def check_range(self, addr_begin, addr_end, as_names):
        try:
            as_result = self.lookup.as_by_ip(str(addr_begin))
            addrs = as_result['net_range'].split('-')

            import ipaddr
            return ipaddr.IPAddress(addr_begin) == ipaddr.IPAddress(addrs[0]) \
               and ipaddr.IPAddress(addr_end) == ipaddr.IPAddress(addrs[1]) \
               and as_names == as_result['as_list']
        except Exception as ex:
            self.err("%s!!!\nunable to detect AS for [%s-%s]; should be: %s" % (ex, addr_begin, addr_end, ",".join(as_names)))

        return False

    def check_addr(self, addr, as_names):
        try:
            as_found = self.lookup.asset(str(addr))
            if (as_names[0] == as_found):
                return 1
            else:
                self.err("wrong AS %s for IP %s; != %s (wanted)" % (as_found, addr, as_names[0]))
        except Exception as ex:
            self.err("%s!!!\nunable to detect AS for IP %s; != %s (wanted)" % (ex, addr, as_names[0]))

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

        print >>sys.stderr, "checking assets from [", args.assets, "]..."
        checker.make_check()
        print >>sys.stderr, "complete."
    except Exception as ex:
        print >>sys.stderr, ">>> FAIL: %s" % ex
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(parse_args()))
