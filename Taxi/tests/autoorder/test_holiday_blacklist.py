import pandas as pd

from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.autoorder.holiday_blacklist import (
    DatesConfig,
    get_holidays_config,
    holidays_blacklist_reducer,
)


def test_dates_config_methods():
    input = {
        '2021-03-14',
        '2021-03-22',
        '2021-03-23',
        '2021-03-29',
        '2021-03-30',
    }
    dates_config = DatesConfig(input)

    assert dates_config._get_replacement_date('2021-03-29') == '2021-03-15'
    assert dates_config._get_replacements_dict() == {
        '2021-03-07': ['2021-03-14'],
        '2021-03-15': ['2021-03-22', '2021-03-29'],
        '2021-03-16': ['2021-03-23', '2021-03-30'],
    }
    assert dates_config.get_blacklist() == input
    assert dates_config.get_replacements('2021-03-07') == ['2021-03-14']
    assert dates_config.get_replacements('2021-03-12') == []


def test_get_holidays_config():
    columns = [
        'organization_id',
        'code',
        'category_id',
        'region_id',
        'utc_dttm_start',
        'utc_dttm_end',
    ]
    data = [
        [1, 1, None, 1, '2021-03-07', '2021-03-07'],
        [1, 1, None, 1, '2021-03-10', '2021-03-12'],
        [3, None, 'a', 1, '2021-03-11', '2021-03-11'],
        [None, None, 'b', 2, '2021-03-10', '2021-03-10'],
        [None, None, 'a', 1, '2021-03-14', '2021-03-14'],
        [2, None, None, 1, '2021-03-09', '2021-03-09'],
        [None, None, None, 1, '2021-03-15', '2021-03-15'],
    ]
    input = pd.DataFrame(data=data, columns=columns)

    expected_output = {
        ('region_id',): {(1,): {'2021-03-15'}},
        ('organization_id',): {(2,): {'2021-03-09', '2021-03-09'}},
        ('region_id', 'category_id'): {
            (2, 'b'): {'2021-03-10'},
            (1, 'a'): {'2021-03-14', '2021-03-14'},
        },
        ('organization_id', 'category_id'): {(3, 'a'): {'2021-03-11'}},
        ('organization_id', 'code'): {
            (1, 1): {'2021-03-07', '2021-03-10', '2021-03-11', '2021-03-12'},
        },
    }
    output = get_holidays_config(input)
    assert output == expected_output


def test_holidays_blacklist_reducer():
    categ_dict = {1: 'a', 2: 'a', 3: 'b', 4: 'b'}
    region_dict = {1: 1, 2: 1, 3: 1, 4: 2}
    holidays_config = {
        ('region_id',): {(1,): {'2021-03-14'}},
        ('organization_id', 'category_id'): {(3, 'a'): {'2021-03-11'}},
        ('organization_id', 'code'): {(1, 1): {'2021-03-07', '2021-03-14'}},
    }
    start_date = '2021-02-28'
    end_date = '2021-03-15'

    test_input = [
        Record(
            code=1,
            organization_id=1,
            date='2021-02-28',
            timestamp=1614470400,
            n_units_of_sku=1,
        ),
        Record(
            code=1,
            organization_id=1,
            date='2021-03-07',
            timestamp=1615075200,
            n_units_of_sku=2,
        ),
        Record(
            code=1,
            organization_id=1,
            date='2021-03-08',
            timestamp=1615161600,
            n_units_of_sku=3,
        ),
        Record(
            code=1,
            organization_id=1,
            date='2021-03-14',
            timestamp=1615680000,
            n_units_of_sku=4,
        ),
        Record(
            code=1,
            organization_id=3,
            date='2021-03-04',
            timestamp=1614816000,
            n_units_of_sku=5,
        ),
        Record(
            code=1,
            organization_id=3,
            date='2021-03-11',
            timestamp=1615420800,
            n_units_of_sku=6,
        ),
        Record(
            code=2,
            organization_id=1,
            date='2021-03-14',
            timestamp=1615680000,
            n_units_of_sku=7,
        ),
        Record(
            code=4,
            organization_id=4,
            date='2021-03-14',
            timestamp=1615680000,
            n_units_of_sku=8,
        ),
    ]

    expected_output = [
        Record(
            code=1,
            organization_id=1,
            date='2021-02-28',
            timestamp=1614470400,
            n_units_of_sku=1,
            replaced=False,
        ),
        Record(
            code=1,
            organization_id=1,
            date='2021-03-07',
            timestamp=1615075200,
            n_units_of_sku=1,
            replaced=True,
        ),
        Record(
            code=1,
            organization_id=1,
            date='2021-03-14',
            timestamp=1615680000,
            n_units_of_sku=1,
            replaced=True,
        ),
        Record(
            code=1,
            organization_id=1,
            date='2021-03-08',
            timestamp=1615161600,
            n_units_of_sku=3,
            replaced=False,
        ),
        Record(
            code=1,
            organization_id=3,
            date='2021-03-04',
            timestamp=1614816000,
            n_units_of_sku=5,
            replaced=False,
        ),
        Record(
            code=1,
            organization_id=3,
            date='2021-03-11',
            timestamp=1615420800,
            n_units_of_sku=5,
            replaced=True,
        ),
        Record(
            code=4,
            organization_id=4,
            date='2021-03-14',
            timestamp=1615680000,
            n_units_of_sku=8,
            replaced=False,
        ),
    ]

    output = []

    job = clusters.MockCluster().job()

    job.table('').label('input').groupby('code', 'organization_id').reduce(
        holidays_blacklist_reducer(
            holidays_config,
            categ_dict,
            region_dict,
            start_date=start_date,
            end_date=end_date,
            date_field='date',
            with_replacement=True,
            split_streams=False,
        ),
    ).put('').label('output')

    job.local_run(
        sources={'input': StreamSource(test_input)},
        sinks={'output': ListSink(output)},
    )
    assert output == expected_output


if __name__ == '__main__':
    test_dates_config_methods()
    test_get_holidays_config()
    test_holidays_blacklist_reducer()
