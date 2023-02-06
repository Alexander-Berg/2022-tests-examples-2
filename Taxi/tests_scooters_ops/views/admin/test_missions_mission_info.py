from tests_scooters_ops import common
from tests_scooters_ops import db_utils
from tests_scooters_ops import utils

HANDLER = '/scooters-ops/v1/admin/missions/mission-info'

MISSION_1 = {
    'tags': ['recharge'],
    'mission_id': 'mission_1',
    'status': 'performing',
    'performer_id': 'performer_1',
    'cargo_claim_id': 'f9082ddf32684d55a575bb23f17150f3',
    'revision': 5,
    'created_at': '2022-01-01T12:00:00.00000+00:00',
    'points': [
        {
            'point_id': 'point_1',
            'type': 'depot',
            'status': 'visited',
            'location': (30.363102, 60.052506),
            'typed_extra': {'depot': {'id': 'depot1'}},
            'order_in_mission': 1,
            'eta': '2022-05-31 08:01:00 +00:00',
            'arrival_time': '2022-05-31 08:00:00 +00:00',
            'address': 'Сиреневый бульвар, 18к1',
            'region_id': 'msk',
        },
        {
            'point_id': 'point_2',
            'type': 'scooter',
            'status': 'arrived',
            'location': (30.37990667, 60.043475),
            'typed_extra': {'scooter': {'id': 'scooter_id_1'}},
            'order_in_mission': 2,
            'eta': '2022-05-31 09:01:00 +00:00',
            'arrival_time': '2022-05-31 09:00:00 +00:00',
            'address': 'улица Брянцева, 2',
            'region_id': 'msk',
        },
        {
            'point_id': 'point_3',
            'type': 'scooter',
            'status': 'planned',
            'location': (30.37990668, 60.043476),
            'typed_extra': {'scooter': {'id': 'scooter_id_2'}},
            'order_in_mission': 3,
            'eta': '2022-05-31 09:00:00 +00:00',
            'address': 'улица Брянцева, 3',
            'region_id': 'msk',
        },
        {
            'point_id': 'point_4',
            'type': 'depot',
            'status': 'planned',
            'location': (30.363102, 60.052506),
            'typed_extra': {'depot': {'id': 'depot1'}},
            'order_in_mission': 4,
            'eta': '2022-05-31 08:00:00 +00:00',
            'address': 'Сиреневый бульвар, 18к1',
            'region_id': 'msk',
        },
    ],
}

HISTORY_1 = [
    {
        'history_timestamp': '2022-05-31 07:00:00 +00:00',
        'mission_id': 'mission_1',
        'type': 'mission_created',
        'extra': {},
    },
    {
        'history_timestamp': '2022-05-31 07:01:00 +00:00',
        'mission_id': 'mission_1',
        'type': 'mission_status_updated',
        'extra': {},
    },
    {
        'history_timestamp': '2022-05-31 07:30:00 +00:00',
        'mission_id': 'mission_1',
        'type': 'mission_started',
        'extra': {},
    },
    {
        'history_timestamp': '2022-05-31 08:00:00 +00:00',
        'mission_id': 'mission_1',
        'point_id': 'point_1',
        'type': 'point_arrived',
        'extra': {},
    },
    {
        'history_timestamp': '2022-05-31 08:05:00 +00:00',
        'mission_id': 'mission_1',
        'point_id': 'point_1',
        'type': 'point_completed',
        'extra': {},
    },
    {
        'history_timestamp': '2022-05-31 09:00:00 +00:00',
        'mission_id': 'mission_1',
        'point_id': 'point_2',
        'type': 'point_arrived',
        'extra': {},
    },
]


@common.TRANSLATIONS
async def test_handler(pgsql, taxi_scooters_ops, mockserver):
    db_utils.add_mission(pgsql, MISSION_1)
    for event in HISTORY_1:
        db_utils.add_history(pgsql, event)

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _profiles_retrieve(request):
        assert request.json['id_in_set'] == ['performer_1']
        assert request.json['projection'] == [
            'data.full_name.first_name',
            'data.full_name.last_name',
            'data.full_name.middle_name',
            'data.park_id',
            'data.uuid',
            'data.phone_pd_ids',
        ]
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'performer_1',
                    'data': {
                        'full_name': {
                            'first_name': '1',
                            'last_name': 'Performer',
                            'middle_name': 'Name',
                        },
                        'park_id': 'park_id',
                        'uuid': 'performer-uuid',
                        'phone_pd_ids': [{'pd_id': 'phone_id'}],
                    },
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _parks_list(request):
        assert request.json['query']['park']['ids'] == ['park_id']
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': '',
                    'name': '',
                    'is_active': True,
                    'city_id': '',
                    'locale': '',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': '',
                    'demo_mode': False,
                    'geodata': {'lon': 12.3, 'lat': 45.6, 'zoom': 11},
                    'provider_config': {'type': 'none', 'clid': 'park-clid'},
                },
            ],
        }

    response = await taxi_scooters_ops.get(
        HANDLER,
        headers={'Accept-Language': 'ru-ru'},
        params={'mission_id': 'mission_1'},
    )

    assert response.status == 200
    assert response.json() == {
        'tabs': {
            'info': {
                'id': 'mission_1',
                'status': {'status': 'performing', 'title': 'Исполняется'},
                'tags': ['recharge'],
                'cargo_claim_id': 'f9082ddf32684d55a575bb23f17150f3',
                'created_at': '2022-01-01T12:00:00+00:00',
                'updated_at': utils.AnyValue(),
                'performer': {
                    'link': (
                        'https://tariff-editor.taxi.yandex-team.ru/'
                        'show-driver/park-clid_performer-uuid'
                    ),
                    'name': 'Performer 1 Name',
                    'phone_pd_id': 'phone_id',
                },
                'points': [
                    {
                        'address': 'Сиреневый бульвар, 18к1',
                        'arrival_time': '2022-05-31T08:00:00+00:00',
                        'eta': '2022-05-31T08:01:00+00:00',
                        'jobs': [],
                        'location': [30.363102, 60.052506],
                        'status': {'status': 'visited', 'title': 'Посещена'},
                        'type': {'title': 'Лавка', 'type': 'depot'},
                    },
                    {
                        'address': 'улица Брянцева, 2',
                        'arrival_time': '2022-05-31T09:00:00+00:00',
                        'eta': '2022-05-31T09:01:00+00:00',
                        'jobs': [],
                        'location': [30.37990667, 60.043475],
                        'status': {
                            'status': 'arrived',
                            'title': 'Курьер прибыл',
                        },
                        'type': {'title': 'Самокат', 'type': 'scooter'},
                    },
                    {
                        'address': 'улица Брянцева, 3',
                        'eta': '2022-05-31T09:00:00+00:00',
                        'jobs': [],
                        'location': [30.37990668, 60.043476],
                        'status': {
                            'status': 'planned',
                            'title': 'Запланирована',
                        },
                        'type': {'title': 'Самокат', 'type': 'scooter'},
                    },
                    {
                        'address': 'Сиреневый бульвар, 18к1',
                        'eta': '2022-05-31T08:00:00+00:00',
                        'jobs': [],
                        'location': [30.363102, 60.052506],
                        'status': {
                            'status': 'planned',
                            'title': 'Запланирована',
                        },
                        'type': {'title': 'Лавка', 'type': 'depot'},
                    },
                ],
                'history': [
                    {
                        'time': utils.AnyValue(),
                        'type': {
                            'title': 'Миссия создана',
                            'type': 'mission_created',
                        },
                    },
                    {
                        'time': utils.AnyValue(),
                        'type': {
                            'title': 'Миссия выполняется',
                            'type': 'mission_started',
                        },
                    },
                    {
                        'time': utils.AnyValue(),
                        'type': {
                            'title': 'Курьер прибыл на точку',
                            'type': 'point_arrived',
                        },
                        'eta': '2022-05-31T08:01:00+00:00',
                    },
                    {
                        'time': utils.AnyValue(),
                        'type': {
                            'title': 'Работы на точке завершены',
                            'type': 'point_completed',
                        },
                    },
                    {
                        'time': utils.AnyValue(),
                        'type': {
                            'title': 'Курьер прибыл на точку',
                            'type': 'point_arrived',
                        },
                        'eta': '2022-05-31T09:01:00+00:00',
                    },
                ],
            },
        },
    }
