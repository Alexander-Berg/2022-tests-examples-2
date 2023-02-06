#!/usr/bin/env python

from __future__ import print_function

import sys
import logging

import tests_base
import svarog
import metrics

AllProviders = [
    metrics.MetricsProvider,
    svarog.SvarogProvider,
]

TestNames = [test.Name for test in AllProviders]


def test_providers(names, config, **args):
    if names:
        providers = [el for el in AllProviders if el.Name in names]
    else:
        providers = AllProviders

    if not providers:
        raise Exception("no test providers found")

    tests = []
    for provider in providers:
        tests.extend(provider.Generate(config=config))

    for t in tests:
        print(t.Name)

    return tests_base.TestsContainer(tests, **args)


def main():
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("--tests")
    parser.add_option("--cache", default="cache")
    parser.add_option("--config", default="../../../WizardQualityTest/config.py")
    parser.add_option("--check", action="store_true")
    parser.add_option("--run", action="store_true")
    parser.add_option("-v", "--verbose", action="store_true")

    (options, args) = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)

    tests = options.tests.split() if options.tests else None
    hosts = map(tests_base.Beta, args)
    if options.config:
        config = eval(open(options.config).read().partition("config =")[-1])
    else:
        config = None

    if options.check:
        provider = test_providers(names=tests, config=config, cachePath=options.cache, cacheOnly=True)
        hosts = provider.Hosts()
        for host in hosts:
            t = provider.RunTest(host)
            provider.CheckTest(t)
    elif options.run:
        with test_providers(names=tests, config=config, cachePath=options.cache, cacheOnly=False) as provider:
            if not hosts:
                hosts = provider.Hosts()

            assert hosts

            errors = provider.Run(*hosts)

            if errors:
                sys.stdout.write("errors:\n%s\n" % "\n".join(errors))
            else:
                sys.stdout.write("OK\n")


if __name__ == "__main__":
    main()
