# pylint: disable=import-only-modules
from datetime import datetime

import pytest

from .utils import select_named


@pytest.mark.pgsql('reposition', files=['drivers.sql', 'mode_home.sql'])
@pytest.mark.now('2020-05-01T00:00:00+0000')
async def test_put(taxi_reposition_api, mockserver, pgsql, testpoint):
    def get_driver_work_modes_():
        return select_named(
            'SELECT driver_id_id, work_mode FROM state.driver_work_modes',
            pgsql['reposition'],
        )

    def get_user_modes_():
        return select_named(
            'SELECT * FROM etag_data.modes', pgsql['reposition'],
        )

    async def put_driver_work_mode_(driver_profile_id, park_db_id, work_mode):
        response = await taxi_reposition_api.put(
            '/internal/reposition-api/v1/service/driver_work_mode?'
            f'driver_profile_id={driver_profile_id}&park_id={park_db_id}',
            json={'work_mode': work_mode},
        )
        assert response.status_code == 200
        assert response.json() == {}

    assert get_driver_work_modes_() == []
    assert get_user_modes_() == []

    await put_driver_work_mode_('driverSS', '1488', 'driver-fix')

    assert get_driver_work_modes_() == [
        {'driver_id_id': 2, 'work_mode': 'driver-fix'},
    ]

    assert get_user_modes_() == [
        {
            'revision': 1,
            'driver_id_id': 2,
            'is_sequence_start': True,
            'valid_since': datetime(2020, 5, 1, 0, 0),
            'data': {},
        },
    ]

    await put_driver_work_mode_('driverSS', '1488', 'orders')

    assert get_driver_work_modes_() == [{'driver_id_id': 2, 'work_mode': None}]

    assert get_user_modes_() == [
        {
            'revision': 2,
            'driver_id_id': 2,
            'is_sequence_start': True,
            'valid_since': datetime(2020, 5, 1, 0, 0),
            'data': {
                'home': {
                    'type': 'free_point',
                    'locations': {},
                    'restrictions': [],
                    'start_screen_subtitle': (
                        '{"tanker_key":"home","is_limitless":false}'
                    ),
                    'start_screen_text': {
                        'subtitle': (
                            '{"tanker_key":"home","is_limitless":false}'
                        ),
                        'title': '{"tanker_key":"home"}',
                    },
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'permitted_work_modes': ['orders'],
                    'tutorial_body': '{"tanker_key":"home"}',
                    'client_attributes': {'dead10cc': 'deadbeef'},
                },
            },
        },
    ]
