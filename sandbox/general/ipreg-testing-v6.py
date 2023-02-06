#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import ipaddr
import json
from functools import partial


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
                        default=25000,
                        help="print '.' for each K-th row; 0 - disable")
    parser.add_argument('--full-check',
                        action='store_true',
                        help="try to check all data instead reg_id only")
    parser.add_argument('--data-version',
                        type=int,
                        default=5,
                        help="if 5 - reliabilities were checked; if 6 - ip-traits")
    parser.add_argument('--attrs-match',
                        default="",
                        help="matching of json-attributes, comma-separated, ${input}:${geo-answer}, use empty value for ${geo-answer} for skipping")
    parser.add_argument('--crash-on-error',
                        action='store_true',
                        help="BOOM-mode")
    args = parser.parse_args()
    return args


def get_corrected_pairs_value(value):
    max_value = 2 ** 16
    value = max(value, 1)
    return min(max_value, value)


stats = {}


def inc_stat_counter(counter_name, value=1):
    stats[counter_name] = stats.get(counter_name, 0) + value


BAD_ID = -5
SPEC_NETS_ID = 99999
YANDEX_REG_ID = 9999
ROOT_ID = 0
EARTH_ID = 10000


def make_reliabilites_hash(traits_json):
    parsed_traits = json.loads(traits_json)

    traits_keys = parsed_traits.keys()
    traits = []

    if 'is_yandex_staff' in traits_keys:
        traits.append({'reliability': 0, 'region_id': 9999})

    if 'region_id' in traits_keys and 'reliability' in traits_keys:
        traits.append({'reliability': int(parsed_traits['reliability']), 'region_id': int(parsed_traits['region_id'])})

    return traits


def parse_traits(json_str):
    traits = json.loads(json_str)

    if traits.get('region_id') and SPEC_NETS_ID == traits['region_id']:
        traits['region_id'] = EARTH_ID
        traits['reserved_net'] = True

    if traits.get('turbo') and traits.get('yandex'):
        traits.pop('yandex')

    return traits


def is_rels_answer_good(wanted_data, got_data):
    return wanted_data == got_data


def is_traits_answer_good(attrs_match, wanted_data, got_data):
    for input_key in wanted_data:
        geo_attr = attrs_match[input_key] if input_key in attrs_match else input_key
        if not geo_attr:
            continue

        if wanted_data[input_key] == 1 and got_data[geo_attr] == True:
            continue

        if wanted_data[input_key] != got_data[geo_attr]:
            print >>sys.stderr, "wanted[%s] => %s != got[%s] => %s" % (input_key, wanted_data[input_key], geo_attr, got_data[geo_attr])
            return False

    return True


def parse_attr_match(attrs_match_str):
    if not attrs_match_str:
        return {}

    matching = {}
    for pair in attrs_match_str.split(','):
        input_attr, geo_attr = pair.split(':')
        matching[input_attr] = geo_attr

    return matching


class Checker(object):
    def __init__(self, args):
        import geobase6
        self.lookup = geobase6.Lookup(args.geodata)

        self.in_stream = sys.stdin if args.ipreg == "-" else open(args.ipreg)
        self.pairs_to_check = get_corrected_pairs_value(args.pairs_check)
        self.debug_progress_step = args.debug_progress_step
        self.crash_mode = args.crash_on_error
        self.attrs_match = parse_attr_match(args.attrs_match)
        self.full_check = args.full_check
        self.data_version = args.data_version

        self.checker_fn = self.lookup.get_region_id_by_ip
        if self.full_check:
            self.checker_fn = self.lookup.get_ip_traits if self.data_version == 6 else self.lookup.get_reliabilities_by_ip
            self.is_answer_good_fn = partial(is_traits_answer_good, self.attrs_match) if self.data_version == 6 else is_rels_answer_good

    def make_check(self):
        for line in self.in_stream:
            inc_stat_counter('rows_total')

            if self.debug_progress_step and (0 == stats['rows_total'] % self.debug_progress_step):
                sys.stderr.write(".")
                if 0 == stats['rows_total'] % 1000000:
                    print "\tM\n"

            self.check_range(line.strip())

        print >>sys.stderr, stats

    def check_range(self, line):
        if not line or line.startswith('#'):
            inc_stat_counter('useless_input')
            return

        addrs_range_str, traits_json_str = line.split('\t')
        addr_lo, addr_hi = addrs_range_str.split('-')

        addr_from = ipaddr.IPAddress(addr_lo)
        if addr_from.version == 6 and addr_from.ipv4_mapped:
            addr_from = addr_from.ipv4_mapped

        addr_to = ipaddr.IPAddress(addr_hi)
        if addr_to.version == 6 and addr_to.ipv4_mapped:
            addr_to = addr_to.ipv4_mapped

        wanted_answer = None
        traits = None

        if self.data_version == 6:
            traits = parse_traits(traits_json_str)
            wanted_answer = traits if self.full_check else int(traits["region_id"])
        else:
            traits = make_reliabilites_hash(traits_json_str)
            wanted_answer = traits if self.full_check else int(traits[0]["region_id"])

        if not traits:
            inc_stat_counter('bad_traits')
            self.err(">>> strange traits-data: %s" % line)
            return

        if not wanted_answer:
            inc_stat_counter('bad_wanted_answer')
            self.err(">>> strange traits-data: %s" % line)
            return

        total_amount = 0
        checked_amount = 0

        while (total_amount < self.pairs_to_check * 2) and (addr_from <= addr_to):
            total_amount += 2
            checked_amount += self.check_addr(addr_from, wanted_answer, self.full_check) + self.check_addr(addr_to, wanted_answer, self.full_check)

            addr_from += 1
            addr_to -= 1

        inc_stat_counter('addrs_qty', total_amount)
        inc_stat_counter('checked_addrs_qty', checked_amount)

        if checked_amount != total_amount:
            inc_stat_counter('failed_lines')
            msg = "non-consistent results were detected!\n%s\n>> result: %d/%d" % (line, checked_amount, total_amount)
            self.err(msg)

    def check_addr(self, addr, wanted_data, full_check):
        result = 0
        got_data = None
        err_msg = ""

        try:
            got_data = self.checker_fn(str(addr))
            if not full_check and wanted_data == got_data:
                result = 1
            if full_check and self.is_answer_good_fn(wanted_data, got_data):
                result = 1
        except Exception as ex:
            err_msg = str(ex)

        if 0 == result:
            self.err("%s [%s] => %s != %s (got/wanted)" % (err_msg, addr, got_data, wanted_data))
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


def start_check():
    return main(parse_args())


if __name__ == "__main__":
    sys.exit(start_check())
