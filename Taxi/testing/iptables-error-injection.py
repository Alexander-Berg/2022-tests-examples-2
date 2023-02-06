#!/usr/bin/env python3.5
# coding: utf8

from __future__ import print_function

import argparse
import subprocess
import random
import time


def handle_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--hostname', help='Hosts to block (can be used multiple times)' +
        ' with optional :port part', required=True, action='append')
    parser.add_argument(
        '--count', help='How many hosts to block per round',
        type=int, default=1)
    parser.add_argument(
        '--verdict', help='What to do with unlucky packets',
        choices=['DROP', 'REJECT'], default='DROP')
    parser.add_argument(
        '--probability', help='Probability of packet drop/reject, ' +
        ' use 1.0 for \'always\'', type=float, default=1.0)
    parser.add_argument(
        '--relax-time', help='Relax time in seconds with no actions',
        type=int, default=10)
    parser.add_argument(
        '--block-time', help='Time with blocking enabled',
        type=int, default=20)
    parser.add_argument(
        '--ipv4', help='Use IPv4', dest='ipv4', action='store_true')
    parser.add_argument(
        '--no-ipv4', help='Don\'t use IPv4', dest='ipv4', action='store_false')
    parser.add_argument(
        '--ipv6', help='Use IPv6', dest='ipv6', action='store_true')
    parser.add_argument(
        '--no-ipv6', help='Don\'t use IPv6', dest='ipv6', action='store_false')
    options = parser.parse_args()
    if not options.ipv6 and not options.ipv4:
        parser.error('You must use either --ipv4 or --ipv6')
    return options


def iptables_action(v, host, block, verdict, probability):
    exe = 'iptables' if v == 4 else 'ip6tables'
    action = '-A' if block else '-D'
    probability_args = [] if probability > 0.999 else [
        '-m', 'statistic',
        '--mode', 'random',
        '--probability', str(probability)]

    reject_args = [] if verdict != 'REJECT' else ['--reject-with', 'tcp-reset']
    cmd = [exe, action, 'INPUT', '-p', 'tcp', '-j', verdict] + \
        probability_args + reject_args

    if ':' in host:
        addr, port = host.split(':', 1)
        cmd += ['-s', addr, '--source-port', port]
    else:
        cmd += ['-s', host]

    print('> {}'.format(' '.join(cmd)))
    subprocess.check_call(cmd)


def block_host(options, host):
    if options.ipv4:
        iptables_action(4, host, True, options.verdict, options.probability)
    if options.ipv6:
        iptables_action(6, host, True, options.verdict, options.probability)


def unblock_host(options, host):
    if options.ipv4:
        iptables_action(4, host, False, options.verdict, options.probability)
    if options.ipv6:
        iptables_action(6, host, False, options.verdict, options.probability)


def loop(options):
    while True:
        hosts = random.sample(options.hostname, options.count)
        print('\nNext round, using hosts: {}'.format(', '.join(hosts)))

        blocked_hosts = []

        try:
            print('=== Block hosts ===')
            for host in hosts:
                block_host(options, host)
                blocked_hosts.append(host)
            print('=== Sleep ===')
            time.sleep(options.block_time)

            print('=== Unblock hosts ===')
            for host in blocked_hosts:
                unblock_host(options, host)
        except:
            print('Caught an exception, unblocking and exiting...')
            for host in blocked_hosts:
                try:
                    unblock_host(options, host)
                except e:
                    print(e)
            raise

        print('=== Sleep ===')
        time.sleep(options.relax_time)


def main():
    options = handle_options()
    loop(options)

if __name__ == '__main__':
    main()
