#!/usr/bin/env python
# -*- coding: utf-8 -*-

# simple IPREG-layout checker


import argparse
import ipaddr
import sys


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--layout',
                        default="layout.json",
                        help="path to all YA networks")
    parser.add_argument('--nets-list',
                        default="all.networks.txt",
                        help="path to all YA networks")
    parser.add_argument('--turbonets-list',
                        default="turbonets.txt",
                        help="path to torbo networks")
    parser.add_argument('--usersnets-list',
                        default="usersnets.txt",
                        help="path to user networks")
    parser.add_argument('--crash-on-error',
                        action='store_true',
                        help="BOOM-mode")
    args = parser.parse_args()
    return args


class IpregWrapper(object):
    def __init__(self, datafile):
        self.lookup = IpregWrapper.init_lookup(datafile)

    @staticmethod
    def init_lookup(datafile):
        import pkgutil
        if not pkgutil.find_loader('ipreg'):
            return None

        import ipreg
        lookup = ipreg.lookup(datafile)
        return lookup


def is_ipv6(addr):
    return -1 != addr.find(':')


def to_ipv6(addr):
    return addr if is_ipv6(addr) else '::ffff:' + addr


def gen_msg(addr, kind):
    msg = "bad result: [%s] is NOT detected as %s-net " % (addr, kind)
    return msg


def is_yandex_net(lookup, host, show_err, crash_flag=False):
    result = lookup.get_net(host)
    if result.is_yandex:
        return True

    msg = gen_msg(host, "YANDEX")
    if crash_flag:
        raise Exception(msg)

    if show_err:
        print msg
        return True

    return False


def is_users_net(lookup, host, show_err, crash_flag=False):
    result = lookup.get_net(host)
    if result.is_user:
        return True

    msg = gen_msg(host, "USER")
    if crash_flag:
        raise Exception(msg)

    if show_err:
        print msg
        return True

    return False


def is_turbo_net(lookup, host, show_err, crash_flag=False):
    foreign_ip = '195.88.112.9'
    headers = {'X-Forwarded-For': foreign_ip}

    result = lookup.get_net_by_headers(host, headers)
    if foreign_ip == result.real_ip and not result.is_yandex:
        return True

    msg = gen_msg(host, "TURBO")
    if crash_flag:
        raise Exception(msg)

    if show_err:
        print msg
        return True

    return False


class Checker(object):
    def __init__(self, layout_json, crash_mode):
        self.crash_mode = crash_mode
        self.lookup = IpregWrapper(layout_json).lookup

    def check_net(self, net_str, func_check, show_err):
        is_ipv6net = is_ipv6(net_str)
        net = ipaddr.IPv6Network(net_str) if is_ipv6net else ipaddr.IPv4Network(net_str)

        total_amount = 0
        ok_amount = 0

        v6_limit = 256
        v6_count = 0

        for host in net.iterhosts():
            total_amount += 1
            if func_check(self.lookup, str(host), show_err, self.crash_mode):
                ok_amount += 1

            if is_ipv6net:  # NB: work-around, because v6-networks TOO LARGE
                v6_count += 1
                if v6_count == v6_limit:
                    break

        if ok_amount != total_amount:
            msg = "non-consistent results were detected!\n" \
                  ">> %s << contains %d hosts. %d/%d checked (ok/total)\n" \
                  % (net_str, net.numhosts, ok_amount, total_amount)

            if self.crash_mode_on:
                raise Exception(msg)

            sys.stderr.write(msg)

    def test_file(self, fname, check_func, show_err=False):
        sys.stdout.write("checking file '%s' via '%s()'... " % (fname, check_func.__name__))

        if not self.lookup:
            if self.crash_mode:
                raise Exception("unable to load ipreg module")
            else:
                print >>sys.stderr, ">>> NO CHECK (unable to load ipreg) <<<"
            return

        for line in open(fname, 'r'):
            network = line.strip()
            self.check_net(network, check_func, show_err)

        print " complete."


RESULT_OK = 0
RESULT_FAIL = 1


def run_full_test(layout_json, nets_list, turbonets_list, usersnets_list, crash_on_error):
    checker = Checker(layout_json, crash_on_error)

    try:
        checker.test_file(nets_list,      is_yandex_net)
        checker.test_file(turbonets_list, is_yandex_net)
        checker.test_file(usersnets_list, is_yandex_net)  # TODO(dieash@) maybe adding ", True)" for LIB-851
        checker.test_file(turbonets_list, is_turbo_net)
        checker.test_file(usersnets_list, is_users_net)

    except Exception as ex:
        print >>sys.stderr, ">>> %s" % ex
        return RESULT_FAIL

    return RESULT_OK


def main(args):
    return run_full_test(args.layout, args.nets_list, args.turbonets_list, args.usersnets_list, args.crash_on_error)


if __name__ == "__main__":
    sys.exit(main(parse_args()))
