import pytest

from tests_blocklist import utils


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'block_key_1.admin': dict(ru='Причина блокировки 1'),
        'blocklist.mechanics.taximeter': dict(ru='Старый ЧС'),
        'blocklist.mechanics.qc_dkvu': dict(ru='Фотоконтроль ВУ'),
        'blocklist.predicates.car_number': dict(ru='По номеру машины'),
        'blocklist.predicates.park_car_number': dict(
            ru='По номеру машины в парке',
        ),
        'blocklist.predicates.license_id': dict(ru='По номеру ВУ'),
        'blocklist.predicates.park_license_id': dict(
            ru='По номеру ВУ в парке',
        ),
        'blocklist.kwargs.car_number': dict(ru='Номер машины'),
        'blocklist.kwargs.park_id': dict(ru='Идентификатор парка'),
        'blocklist.kwargs.license_id': dict(ru='Идентификатор ВУ'),
    },
)
async def test_admin_settings(taxi_blocklist):
    response = await taxi_blocklist.get(
        '/admin/blocklist/v1/settings', headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    reasons = [dict(code='block_key_1', description='Причина блокировки 1')]
    assert response.json() == {
        'mechanics': [
            {
                'description': 'Старый ЧС',
                'id': 'taximeter',
                'predicates': [
                    {
                        'predicate_id': utils.Predicates.PARK_CAR_NUMBER,
                        'reasons': reasons,
                    },
                    {
                        'predicate_id': utils.Predicates.CAR_NUMBER,
                        'reasons': reasons,
                    },
                ],
            },
            {
                'description': 'Фотоконтроль ВУ',
                'id': 'qc_dkvu',
                'predicates': [
                    {
                        'predicate_id': utils.Predicates.PARK_CAR_NUMBER,
                        'reasons': reasons,
                    },
                ],
            },
        ],
        'predicates': [
            {
                'description': 'По номеру машины',
                'id': utils.Predicates.CAR_NUMBER,
                'kwargs': [{'code': 'car_number', 'name': 'Номер машины'}],
            },
            {
                'description': 'По номеру машины в парке',
                'id': utils.Predicates.PARK_CAR_NUMBER,
                'kwargs': [
                    {'code': 'park_id', 'name': 'Идентификатор парка'},
                    {'code': 'car_number', 'name': 'Номер машины'},
                ],
            },
            {
                'description': 'По номеру ВУ',
                'id': utils.Predicates.LICENSE,
                'kwargs': [{'code': 'license_id', 'name': 'Идентификатор ВУ'}],
            },
            {
                'description': 'По номеру ВУ в парке',
                'id': utils.Predicates.PARK_LICENSE,
                'kwargs': [
                    {'code': 'park_id', 'name': 'Идентификатор парка'},
                    {'code': 'license_id', 'name': 'Идентификатор ВУ'},
                ],
            },
        ],
    }
