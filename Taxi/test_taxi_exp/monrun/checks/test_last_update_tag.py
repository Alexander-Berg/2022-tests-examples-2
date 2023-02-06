import collections

import pytest

from taxi_exp.monrun import main


@pytest.yield_fixture(autouse=True)
def clean_monrun_errors():
    yield
    main.MONRUN_ERRORS = collections.defaultdict(set)


@pytest.mark.parametrize(
    'tag,expected_answer',
    [
        (None, '1; Tag None is never updated'),
        ('normal_filled_tag', '0; Tag normal_filled_tag updated'),
        (
            'warn_filled_tag',
            '1; The last warn_filled_tag update was a long time ago 14400',
        ),
        (
            'crit_filled_tag',
            '2; The last crit_filled_tag update was a long time ago 21600',
        ),
        ('no_filled_tag', '1; Tag no_filled_tag is never updated'),
    ],
)
@pytest.mark.usefixtures('taxi_exp_client')
@pytest.mark.config(
    EXP_MONITORING_SETTINGS={
        'last_update_tags': {
            'default': {
                'crit_threshold': {'value': 21600, 'level': 2},
                'warn_threshold': {'value': 14400, 'level': 1},
            },
        },
    },
)
@pytest.mark.pgsql('taxi_exp', files=['fill_history.sql'])
def test_send_tagname_last_update_tag(tag, expected_answer, capsys):
    main.run(['last_update_tag', '--tag', tag])

    out, err = capsys.readouterr()
    out = out.strip()
    err = err.strip()

    assert not err
    assert out == expected_answer
