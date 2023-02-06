#!/usr/bin/env python3

def _raise(t):
    raise t('test')


def test_base(tap):
    with tap.plan(16, 'test set'):
        tap.passed('Test passed')


        tap.ok(True, 'Tap.ok test passed')
        tap.isa_ok(True, bool, 'Tap.isa_ok passed')
        tap.is_ok(True, True, 'Tap.is_ok passed')
        tap.isnt_ok(True, 1, 'Tap.isnt_ok passed')
        tap.eq_ok(True, 1, 'Tap.eq_ok passed')
        tap.ne_ok(True, False, 'Tap.ne_ok passed')

        tap.in_ok(True, (False, True), 'Tap.in_ok passed')
        tap.not_in_ok(2, (False, True), 'Tap.not_in_ok passed')

        tap.import_ok('sys', 'Tap.import_ok')

        tap.like('Hello, world', r'w[oO]rld', 'Tap.like')
        tap.unlike('Hello, world', r'w0rld', 'Tap.unlike')

        tap.exception_ok(lambda: _raise(ValueError),
                         ValueError, 'Tap.exception_ok')

        with tap.subtest(2, 'subtest') as tapw:
            tapw.passed('test in subtest')
            tapw.ok(True, 'subtest.ok')
            tapw.diag('test diagnostic message')
            tapw.note('test note message')

        with tap.subtest(None, 'subtest without plan') as tapw:
            tapw.passed('test in subtest')
            tapw.ok(True, 'subtest.ok')

        with tap.subtest() as tapw:
            tapw.passed('test in subtest')
            tapw.ok(True, 'subtest.ok')
