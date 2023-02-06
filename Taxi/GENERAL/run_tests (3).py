# pylint: skip-file
# flake8: noqa

"""
Runs tests for all versions available in migrations_tools.migrator
"""

import json
import os

from migration_tools import migrator
from migration_tools import utils


# DIrectory for tests input and expected result
TESTS_DIR = os.path.join(
    utils.SERVICES_PATH, 'geo-pipeline-control-plane/scripts/migration/tests',
)


def run_tests():
    print('Start running tests...')

    for version in migrator.get_all_available_versions():
        input_data = json.load(
            open(os.path.join(TESTS_DIR, f'input_{version}.json'), 'r'),
        )
        expected = json.load(
            open(os.path.join(TESTS_DIR, f'expected_{version}.json'), 'r'),
        )
        if not input_data:
            print()

        for name in input_data.keys():
            result = migrator.migrate(input_data[name], version)
            if result != expected[name]:
                print(
                    f"""
    {result}
    not equeal
    {expected[name]}
    for version {version}, name {name}
                """,
                )

    print('Finished')


if __name__ == '__main__':
    run_tests()
