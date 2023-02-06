import sys
import argparse
from robot.research.alignment.alignment import BestAlignment


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prod', required=True, help='path to current prod formula')
    parser.add_argument('--exp', required=True, help='path to candidate formula')
    args = parser.parse_args()

    res = BestAlignment(args.prod.split(), args.exp.split())
    for r in res:
        print r.decode('utf-8')

if __name__ == '__main__':
    sys.exit(main())
