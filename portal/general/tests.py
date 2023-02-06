# -*- coding: utf-8 -*-

__author__ = "Zasimov Alexey"
__email__ = "zasimov-a@yandex-team.ru"

u"""
В отличие от cover сверяет не все поля, а только те, что есть в тесте.
"""

from cover import cover, left_dicts_equals

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 5:
        print "usage : %s browser.xml profiles.xml extra.xml cover.xml" % sys.argv[0]
        exit(2)
    r = 0
    for x in cover(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], left_dicts_equals):
        r = 1
    exit(r)
