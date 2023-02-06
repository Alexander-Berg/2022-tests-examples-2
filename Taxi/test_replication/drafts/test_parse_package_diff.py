# pylint: disable=protected-access
import pytest

from replication.drafts.models.helpers import parse_package


@pytest.mark.parametrize(
    'active_package, active_version, payload, expected, limit',
    [
        (
            'yandex-taxi-dmp-rules',
            '0.0.694testing2375',
            {
                'package': 'yandex-taxi-dmp-rules',
                'version': '0.0.694testing2375',
            },
            (
                'yandex-taxi-dmp-rules (0.0.694testing2375)\n\n'
                'CURRENT DEVELOP\n\n'
                '* Foo Bar | some: text, text, text '
                'https://a.yandex-team.ru/review/1\n\n'
                'PR foo@ "some text: and text '
                'https://a.yandex-team.ru/review/2":\n\n'
                'PR foo@ "some text: text text text/text text '
                'https://a.yandex-team.ru/review/3":\n\n'
                'PR foo@ "some text: text text text text text. '
                'https://a.yandex-team.ru/review/4":\n\n'
                'PR foo@ "some text: text text… '
                'https://a.yandex-team.ru/review/5":'
            ),
            30,
        ),
        (
            'yandex-taxi-dmp-rules',
            '0.0.548',
            {
                'package': 'yandex-taxi-dmp-rules',
                'version': '0.0.694testing2375',
            },
            (
                'yandex-taxi-dmp-rules (0.0.694testing2375)\n\n'
                'CURRENT DEVELOP\n\n'
                '* Foo Bar | some: text, text, text '
                'https://a.yandex-team.ru/review/1\n\n'
                'PR foo@ "some text: and text '
                'https://a.yandex-team.ru/review/2":\n\n'
                'PR foo@ "some text: text text text/text text '
                'https://a.yandex-team.ru/review/3":\n\n'
                'PR foo@ "some text: text text text text text. '
                'https://a.yandex-team.ru/review/4":\n\n'
                'PR foo@ "some text: text text… '
                'https://a.yandex-team.ru/review/5":'
            ),
            50,
        ),
        (
            'yandex-taxi-dmp-rules',
            '0.0.694testing2375',
            {
                'package': 'yandex-taxi-dmp-rules',
                'version': '0.0.694testing2375',
            },
            (
                'yandex-taxi-dmp-rules (0.0.694testing2375)\n\n'
                'CURRENT DEVELOP\n\n'
                '* Foo Bar | some: text, text, text '
                'https://a.yandex-team.ru/review/1\n\n'
                'PR foo@ "some text: and text '
                'https://a.yandex-team.ru/review/2":\n\n'
                'PR foo@ "some text: text text text/text text '
                'https://a.yandex-team.ru/review/3":\n\n'
                '...truncated'
            ),
            5,
        ),
    ],
)
def test_parse_package_test_diff(
        get_file_path,
        active_package,
        active_version,
        payload,
        expected,
        limit,
):
    result = parse_package.parse_package_test(
        get_file_path('test_example_changelog'),
        active_package=active_package,
        active_version=active_version,
        payload=payload,
        limit=limit,
    )
    assert result == expected


@pytest.mark.parametrize(
    'active_package, active_version, payload, expected, limit',
    [
        (
            'yandex-taxi-dmp-rules',
            '0.0.547',
            {'package': 'yandex-taxi-dmp-rules', 'version': '0.0.549'},
            'yandex-taxi-dmp-rules (0.0.549)\n\n...truncated',
            1,
        ),
        (
            'yandex-taxi-dmp-rules',
            '0.0.548',
            {'package': 'yandex-taxi-dmp-rules', 'version': '0.0.549'},
            (
                'yandex-taxi-dmp-rules (0.0.549)\n\n'
                '* Foo Bar | feat XXX: YYY '
                'https://a.yandex-team.ru/review/1\n\n'
                '* Foo Bar | feat XXX: YYY '
                'https://a.yandex-team.ru/review/2'
            ),
            22,
        ),
        (
            'yandex-taxi-dmp-rules',
            '0.0.547',
            {'package': 'yandex-taxi-dmp-rules', 'version': '0.0.549'},
            (
                'yandex-taxi-dmp-rules (0.0.549)\n\n'
                '* Foo Bar | feat XXX: YYY '
                'https://a.yandex-team.ru/review/1\n\n'
                '* Foo Bar | feat XXX: YYY '
                'https://a.yandex-team.ru/review/2\n\n'
                'yandex-taxi-dmp-rules (0.0.548)\n\n'
                '* Foo Bar | feat replication_rules: YYY '
                'https://a.yandex-team.ru/review/5'
            ),
            22,
        ),
    ],
)
def test_parse_package_prod_diff(
        get_file_path,
        active_package,
        active_version,
        payload,
        expected,
        limit,
):
    result = parse_package.parse_package_prod(
        get_file_path('prod_example_changelog'),
        active_package=active_package,
        active_version=active_version,
        payload=payload,
        limit=limit,
    )
    assert result == expected
