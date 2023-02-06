# pylint: disable=redefined-outer-name
import datetime

import pytest

from fleet_fines.generated.cron import cron_context as context_module
from fleet_fines.generated.cron import run_cron
from fleet_fines.yt_access import drivers_docs_source as dds


@pytest.mark.config(FLEET_FINES_ACTUALIZE_DLS={'is_enabled': True})
@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
        (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
         is_normalized, is_valid, source_modified_date)
    VALUES
        ('p1', 'd1', '0000000000', '0000000000',
         TRUE, FALSE, '2020-01-01'),
        ('p2', 'd2', '1111111111', '1111111111',
         TRUE, TRUE, '2020-01-02')
    """,
    ],
)
@pytest.mark.now('2020-05-09T00:00')
async def test_actualize_dl(cron_context: context_module.Context, patch):
    @patch(
        'fleet_fines.yt_access.drivers_docs_source.'
        'DriversDocsSource.get_recent_docs',
    )
    def _get_docs(min_ride_time):
        assert min_ride_time == datetime.datetime(2020, 2, 9, 0, 0)
        yield from [
            dds.DriverDoc(
                park_id='p1',
                driver_id='d1',
                dl_pd_id_original='0000000000',
                modified_date=datetime.datetime(2020, 1, 3),
                last_ride_time=datetime.datetime(2020, 1, 2),
            ),
            dds.DriverDoc(
                park_id='p2',
                driver_id='d2',
                dl_pd_id_original='1212121212',
                modified_date=datetime.datetime(2020, 1, 3),
                last_ride_time=datetime.datetime(2020, 1, 2),
            ),
            dds.DriverDoc(
                park_id='p3',
                driver_id='d3',
                dl_pd_id_original='3333333333',
                modified_date=datetime.datetime(2020, 1, 3),
                last_ride_time=datetime.datetime(2020, 1, 2),
            ),
        ]

    await run_cron.main(['fleet_fines.crontasks.actualize_dl', '-t', '0'])

    rows = await cron_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.documents_dl',
    )
    data = []
    for row in rows:
        row_data = dict(row)
        assert row_data.pop('modified_at')
        data.append(row_data)

    expected = [
        {
            'id': 1,
            'park_id': 'p1',
            'driver_id': 'd1',
            'dl_pd_id_original': '0000000000',
            'dl_pd_id_normalized': '0000000000',
            'is_normalized': True,
            'is_valid': False,
            'last_check_date': None,
            'last_successful_check': None,
            'source_modified_date': datetime.datetime(2020, 1, 3, 0, 0),
            'last_ride_time': datetime.datetime(2020, 1, 2, 0, 0),
        },
        {
            'id': 2,
            'park_id': 'p2',
            'driver_id': 'd2',
            'dl_pd_id_original': '1212121212',
            'dl_pd_id_normalized': None,
            'is_normalized': False,
            'is_valid': False,
            'last_check_date': None,
            'last_successful_check': None,
            'source_modified_date': datetime.datetime(2020, 1, 3, 0, 0),
            'last_ride_time': datetime.datetime(2020, 1, 2, 0, 0),
        },
        {
            'id': 5,
            'park_id': 'p3',
            'driver_id': 'd3',
            'dl_pd_id_original': '3333333333',
            'dl_pd_id_normalized': None,
            'is_normalized': False,
            'is_valid': False,
            'last_check_date': None,
            'last_successful_check': None,
            'source_modified_date': datetime.datetime(2020, 1, 3, 0, 0),
            'last_ride_time': datetime.datetime(2020, 1, 2, 0, 0),
        },
    ]
    assert data == expected
