def mock_personal_license_find(mockserver, license_pd_id):
    """mock personal client"""

    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def foo_handler(request):  # pylint: disable=unused-variable
        return {'id': license_pd_id, 'value': request.json['value']}


def mock_fleet_vehicles_retrieve(mockserver, park_id, car_id):
    @mockserver.json_handler(
        '/fleet-vehicles/v1/vehicles/retrieve_by_number_with_normalization',
    )  # pylint: disable=unused-variable
    def vehicles_handler(request):  # pylint: disable=unused-variable
        return {
            'vehicles': [
                {
                    'park_id_car_id': f'{park_id}_{car_id}',
                    'data': {
                        'park_id': park_id,
                        'car_id': car_id,
                        'number_normalized': 'x124yy777',
                    },
                },
            ],
        }


def mock_driver_profiles_retrieve(mockserver, park_id, car_id, driver_id):
    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings'
        '/drivers/retrieve_by_park_id_car_id',  # noqa pylint: disable=unused-variable
    )
    def profiles_handler(request):  # pylint: disable=unused-variable
        return {
            'profiles_by_park_id_car_id': [
                {
                    'park_id_car_id': f'{park_id}_{car_id}',
                    'profiles': [
                        {
                            'park_driver_profile_id': f'{park_id}_{driver_id}',
                            'data': {
                                'uuid': driver_id,
                                'work_status': 'working',
                                'park_id': park_id,
                            },
                        },
                    ],
                },
            ],
        }


def mock_qc_state(mockserver, park_id, car_id, pass_id):
    @mockserver.json_handler(
        '/quality-control/api/v1/state',
    )  # noqa pylint: disable=unused-variable
    def qc_state_handler(request):  # pylint: disable=unused-variable
        return {
            'items': [
                {'entity_id': f'{park_id}_{car_id}', 'pass_id': pass_id},
            ],
        }


def mock_qc_settings(mockserver):
    @mockserver.json_handler(
        '/quality-control-py3/api/v1/settings/entity',
    )  # noqa pylint: disable=unused-variable
    def qc_settings_handler(request):  # pylint: disable=unused-variable
        driver_exams = [
            {
                'code': 'dkk',
                'block': {'sanctions': ['orders_off'], 'release': '123'},
                'pass': {'stale': '1h', 'filter': [{'field': '123'}]},
                'media': {
                    'items': [{'code': 'front', 'type': '123'}],
                    'stale': '1h',
                    'url_expire': '1h',
                    'default': ['123'],
                },
            },
            # {'code': 'dkvu', 'block': {'sanctions': ['orders_off']}},
            # {'code': 'identity', 'block': {'sanctions': ['orders_off']}},
            # {'code': 'biometry', 'block': {'sanctions': ['orders_off']}},
        ]
        car_exams = [
            {
                'code': 'dkb',
                'block': {'sanctions': ['lightbox_off', 'sticker_off']},
            },
            {'code': 'sts', 'block': {'sanctions': ['orders_off']}},
        ]
        if request.args['type'] == 'driver':
            return driver_exams
        return car_exams
