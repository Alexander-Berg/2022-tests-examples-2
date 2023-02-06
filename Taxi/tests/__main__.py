import argparse

from tools.teamcity.tests import execute_tests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--upload-config', action='store_true')
    parser.add_argument('--force-install', action='store_true')
    args = parser.parse_args()
    execute_tests(args.upload_config, args.force_install)


if __name__ == '__main__':
    main()
