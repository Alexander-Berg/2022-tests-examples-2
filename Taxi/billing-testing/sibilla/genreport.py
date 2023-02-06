#!/usr/bin/env python
# coding: utf8

import argparse
import os.path
import sys

from sibilla import reporter
from sibilla import storage

RESULTS_DATABASE_NAME = 'results.sqlite3'


def get_path() -> str:
    parser = argparse.ArgumentParser(description='General Report Generator')
    parser.add_argument('path', help='artifacts directory path')
    args = parser.parse_args()
    return args.path


def generate(output: str) -> None:
    db_path = os.path.join(output, RESULTS_DATABASE_NAME)
    if not os.path.exists(db_path):
        print(f'database "{db_path}" does not exists', file=sys.stderr)
        sys.exit(2)
    stg = storage.Storage(filename=db_path)
    report_fname = reporter.generate_general_report(outdir=output, stg=stg)
    print(f'report generated to file {report_fname}')


generate(os.path.abspath(os.path.join(get_path(), 'output')))
