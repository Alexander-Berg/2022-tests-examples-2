import sys


def test_version(tap):
    with tap.plan(1):
        major = sys.version_info[0]
        minor = sys.version_info[1]
        micro = sys.version_info[2]
        tap.eq_ok((major, minor, micro), (3, 7, 3), 'Correct python')
