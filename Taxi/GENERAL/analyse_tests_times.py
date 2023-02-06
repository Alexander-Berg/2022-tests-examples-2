import argparse
import collections
import operator
import pathlib
from typing import Dict
from typing import List
from typing import Optional
from xml.etree import ElementTree as xml_tree

FIXTURE_TAG = 'property'
TEST_TAG = 'testcase'


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    times_by_tests: Dict[str, float] = {}
    times_by_fixtures: Dict[str, float] = {}
    calls_numbers_by_fixtures: collections.Counter = collections.Counter()

    for report_path in args.reports_dir.glob('junit-*.xml'):
        doc_root = xml_tree.parse(str(report_path)).getroot()
        for doc_element in doc_root.iter():
            if doc_element.tag == TEST_TAG:
                test_name = parse_test_name(doc_element)
                test_time = float(doc_element.attrib['time'])
                times_by_tests[test_name] = test_time
            elif doc_element.tag == FIXTURE_TAG:
                fixture_name = parse_fixture_name(doc_element)
                if fixture_name is None:
                    continue
                fixture_time = float(doc_element.attrib['value'])
                times_by_fixtures.setdefault(fixture_name, 0)
                times_by_fixtures[fixture_name] += fixture_time
                calls_numbers_by_fixtures[fixture_name] += 1

    print_table(
        times_by_tests,
        times_by_fixtures,
        calls_numbers_by_fixtures,
        args.limit,
    )


def parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--reports-dir',
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help='Path to directory with junit reports',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=-1,
        help='Show no more \'limit\' the longest tests and fixtures',
    )

    return parser.parse_args(argv)


def parse_test_name(doc_element: xml_tree.Element) -> str:
    return '.'.join(
        (doc_element.attrib['classname'], doc_element.attrib['name']),
    )


def parse_fixture_name(doc_element: xml_tree.Element) -> Optional[str]:
    base_name = doc_element.attrib['name']
    name = base_name.rsplit('_setup_time', maxsplit=1)[0]
    if name in (base_name, 'total'):
        return None
    return name


def print_table(
        times_by_tests: Dict[str, float],
        times_by_fixtures: Dict[str, float],
        calls_numbers_by_fixtures: collections.Counter,
        limit: int,
) -> None:
    if not times_by_tests and not times_by_fixtures:
        print('No tests or fixtures')
        return

    sorted_times_by_tests = sorted(
        times_by_tests.items(), key=operator.itemgetter(1), reverse=True,
    )
    print('{:<128} {}'.format('Test name', 'Total duration (s)'))
    for test_name, test_time in sorted_times_by_tests[:limit]:
        # logger.info('%-128s %.6f', test_name, test_time)
        print(f'{test_name:<128} {test_time:.6f}')

    print('\n')

    sorted_times_by_fixtures = sorted(
        times_by_fixtures.items(), key=operator.itemgetter(1), reverse=True,
    )
    print(
        '{:<40} {:<24} {}'.format(
            'Fixture name', 'Average duration (s)', 'Total duration (s)',
        ),
    )
    for fixture_name, fixture_time in sorted_times_by_fixtures[:limit]:
        avg_time = fixture_time / calls_numbers_by_fixtures[fixture_name]
        print(f'{fixture_name:<40} {avg_time:<24.6f} {fixture_time:.6f}')


if __name__ == '__main__':
    main()
