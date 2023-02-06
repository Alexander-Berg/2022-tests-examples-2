# pylint: disable=redefined-outer-name,invalid-name
import datetime as dt
import typing

from aiohttp import web
import pytest

import driver_referrals.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['driver_referrals.generated.service.pytest_plugins']

COMMON_DRIVER_HEADERS = {
    'X-Request-Application-Version': '9.57',
    'X-Request-Platform': 'android',
    'Accept-Language': 'ru',
    'User-Agent': 'Taximeter 9.05 (1234)',
}

TRANSLATIONS = {
    'bucket_driver_bonus': {'ru': 'Бонус'},
    'bucket_driver_completed': {'ru': 'Выполнено'},
    'bucket_driver_finish_before': {'ru': 'Успеть до'},
    'bucket_driver_requirements_title': {'ru': 'Условия для друга'},
    'bucket_driver_rule_regions': {'ru': 'Заказы в регионе'},
    'bucket_received': {'ru': 'Получено'},
    'bucket_status_awaiting_payment': {'ru': 'Ожидает выплаты'},
    'bucket_status_failed': {'ru': 'Условия не выполнены'},
    'bucket_status_in_progress': {'ru': '{completed} из {required}'},
    'bucket_status_waiting_for_rule': {
        'ru': 'Не приступил к выполнению реферальной программы',
    },
    'bucket_title': {'ru': 'Пригласи друга'},
    'bucket_title_invites': {'ru': 'Приглашения'},
    'bucket_your_code': {'ru': 'Ваш код'},
    'driver_screen_button_subtitle': {'ru': 'Стать водителем'},
    'driver_screen_button_title': {'ru': 'Пригласи друга'},
    'bucket_help_main_text': {'ru': 'Тут описание рефералки'},
    'bucket_help_requirement_elem1': {'ru': 'Первая причина это ты'},
    'bucket_help_requirement_elem2': {'ru': 'Вторая причина это не ты'},
    'bucket_help_requirement_elem3': {'ru': 'Все из-за денег'},
    'bucket_help_requirement_title': {'ru': 'Почему и зачем?'},
    'bucket_help_rules_template': {
        'ru': (
            '**C {start_time} по {end_time}, бонус {bonus}:** надо совершить'
            ' {rides} поездок {days} дней в регионах: **{regions}**'
        ),
    },
    'bucket_help_rules_title': {'ru': 'Правила'},
    'bucket_help_title': {'ru': 'Пригласи друга по рефералке'},
    'bucket_main_text': {'ru': 'Можно приглашать друзей'},
    'check_promocode_ok': {'ru': 'Промокод ок'},
    'check_promocode_error': {'ru': 'Промокод не тот'},
    'bucket_days_left': {'ru': 'Осталось дней: {}'},
    'bucket_days_to_complete_after_first_order': {
        'ru': 'Выполнить за {} дней после первого доставленного заказа',
    },
    'bucket_less_than_day_left': {'ru': 'Осталось менее дня'},
    'share_code_format': {'ru': 'Мой реферальный код - {code}, {link}'},
    'filter_waiting': {'ru': 'Ещё не начали'},
    'filter_in_progress': {'ru': 'Выполняют заказы'},
    'filter_completed': {'ru': 'Выполнили все условия'},
    'filter_all': {'ru': 'Все друзья'},
    'invite': {'ru': 'Пригласить друга'},
    'just_invite': {'ru': 'Пригласить'},
    'invite_more': {'ru': 'Пригласить ещё'},
    'no_completed_orders': {'ru': 'Ещё не начал выполнять заказы'},
    'received': {'ru': 'Получено'},
    'code_title': {'ru': 'Код для друзей'},
    'rides_count': {'ru': '{} заказа'},
    'promocode': {'ru': 'Промокод'},
    'completed_orders': {'ru': 'Выполнено заказов'},
    'bonus': {'ru': 'Бонус'},
    'tariffs': {'ru': 'Тарифы'},
    'write_message': {'ru': 'Написать сообщение'},
    'conditions': {'ru': 'Условия'},
    'zone_count': {'ru': '{} регион'},
    'tariff_count': {'ru': '{} тариф'},
    'promocode_detail': {'ru': 'Смена'},
    'promocode_subdetail': {'ru': 'без комиссии'},
    'default_text': {
        'ru': (
            'Пригласите друзей и получите до {amount}. Им нужно'
            ' будет зарегистрироваться и начать выполнять'
            ' заказы.'
        ),
    },
    'your_friend': {'ru': 'Ваш Друг'},
    'your_friend_in_park': {'ru': 'Ваш Друг в парке'},
    'your_friend_in_same_park': {'ru': 'Ваш друг в вашем парке'},
    'your_friend_in_other_park': {'ru': 'Ваш друг в другом парке'},
    'your_friend_selfemployed': {'ru': 'Ваш самозанятый друг'},
    'driver': {'ru': 'Водитель'},
    'driver_in_park': {'ru': 'Водитель в парке'},
    'driver_in_same_park': {'ru': 'Водитель в вашем парке'},
    'driver_in_other_park': {'ru': 'Водитель в другом парке'},
    'driver_selfemployed': {'ru': 'Самозанятый водитель'},
    'courier': {'ru': 'Курьер'},
    'eda_courier': {'ru': 'Курьер Еды'},
    'lavka_courier': {'ru': 'Курьер Лавки'},
    'all_tariffs': {'ru': 'Все тарифы'},
    'courier_selfemployed': {'ru': 'Самозанятый курьер'},
    'all_tariffs_except': {'ru': 'Все тарифы, кроме: {excluded}'},
    'share_title_default': {'ru': 'Подключайся к Яндекс.Про'},
    'share_description_default': {'ru': 'С кодом {code}'},
    'share_site_title_default': {'ru': 'Яндекс.Про'},
    'current_rules': {'ru': 'Текущие правила программы'},
    'notification.rule_assigned.title': {'ru': 'Заголовок rule_assigned'},
    'notification.rule_assigned.text': {'ru': 'Текст rule_assigned'},
    'notification.daily_stats_updated.title': {
        'ru': 'Заголовок daily_stats_updated',
    },
    'notification.daily_stats_updated.text': {
        'ru': 'Текст daily_stats_updated',
    },
    'notification.payments_created.title': {
        'ru': 'Заголовок payments_created',
    },
    'notification.payments_created.text': {'ru': 'Текст payments_created'},
    'notification.create_new_account.title': {
        'ru': 'Заголовок create_new_account',
    },
    'notification.create_new_account.text': {'ru': 'Текст create_new_account'},
    'notification.add_referral.title': {'ru': 'Заголовок add_referral'},
    'notification.add_referral.text': {'ru': 'Текст add_referral'},
    'notification.rules_updated.text': {'ru': 'Текст rules_updated'},
    'notification.rules_updated.title': {'ru': 'Заголовок rules_updated'},
    'create_payments_eats_adjustment_comment': {
        'ru': 'Выплата реферального бонуса за {}',
        'en': 'Payout of referral bonus for {}',
    },
    'remind_friend': {'ru': 'Напомнить другу'},
    'invitation_text_for_taxi_drivers': {
        'ru': 'Мой реферальный код - {code}, {link}',
    },
    'reminder_text_for_taxi_drivers': {
        'ru': 'Друг, заводи уже, поехали деньги зарабатывать',
    },
    'invitation_text_for_eda_couriers': {
        'ru': 'Мой реферальный код - {code}, {link}',
    },
    'reminder_text_for_eda_couriers': {
        'ru': 'Друг, бери коробку, пошли разносить еду',
    },
    'invitation_text_for_lavka_couriers': {
        'ru': 'Мой реферальный код - {code}, {link}',
    },
    'reminder_text_for_lavka_couriers': {
        'ru': 'Друг, бери коробку, пошли разносить продукты',
    },
    'invitation_text_for_couriers': {
        'ru': 'Мой реферальный код - {code}, {link}',
    },
    'reminder_text_for_couriers': {
        'ru': 'Друг, бери коробку, пошли разносить заказы',
    },
}

TRANSLATIONS_GEOAREAS = {
    'moscow': {'ru': 'Москва'},
    'kaluga': {'ru': 'Калуга'},
    'tula': {'ru': 'Тула'},
    'riga': {'ru': 'Рига'},
}

TRANSLATIONS_TARIFF = {
    'currency_sign.rub': {'ru': '₽'},
    'currency_sign.eur': {'ru': '€'},
    'old_category_name.eda': {'ru': 'Обычный'},
    'old_category_name.econom': {'ru': 'Эконом'},
    'old_category_name.business': {'ru': 'Комфорт'},
    'old_category_name.comfortplus': {'ru': 'Комфорт+'},
    'old_category_name.minivan': {'ru': 'Минивэн'},
    'old_category_name.vip': {'ru': 'Бизнес'},
    'old_category_name.ultimate': {'ru': 'Premier'},
    'old_category_name.maybach': {'ru': 'Élite'},
}

TRANSLATIONS_NOTIFY = {
    'helpers.month_1_part': {'ru': 'янв'},
    'helpers.month_4_part': {'ru': 'апр'},
    'helpers.month_5_part': {'ru': 'май'},
    'helpers.month_12_part': {'ru': 'дек'},
}


@pytest.fixture
def simple_secdist(simple_secdist, pgsql):
    hosts = ' '.join(
        f'{k}={v}'
        for k, v in pgsql['driver_referrals'].conn.get_dsn_parameters().items()
        if k in ('host', 'port', 'user', 'password', 'dbname')
    )
    simple_secdist['postgresql_settings']['databases']['driver_referrals'] = [
        {'shard_number': 0, 'hosts': [hosts]},
    ]
    simple_secdist['settings_override']['ORDERS_API_TOKEN'] = ''
    simple_secdist['settings_override']['STARTRACK_API_PROFILES'] = {
        'driver-referrals': {
            'url': 'http://startrack/',
            'org_id': 0,
            'oauth_token': 'STARTRACK_TOKEN',
        },
    }
    simple_secdist['settings_override']['YQL_TOKEN'] = ''
    return simple_secdist


@pytest.fixture
def mock_driver_profiles_drivers_profiles(mock_driver_profiles):
    def _mock_driver_profiles_drivers_profiles(
            *,
            eats_keys: typing.Dict[str, int],
            nonexistent_drivers: typing.Container[str] = (),
            nonexistent_parks: typing.Container[str] = (),
    ):
        @mock_driver_profiles('/v1/driver/profiles/retrieve')
        def _(request):
            id_in_set = request.json['id_in_set']
            profiles = []
            for park_driver_profile_id in id_in_set:
                park_id, driver_id = park_driver_profile_id.split('_')
                if (
                        driver_id in nonexistent_drivers
                        or park_id in nonexistent_parks
                ):
                    continue
                elif driver_id in eats_keys:
                    data = {
                        'park_id': park_id,
                        'uuid': driver_id,
                        'external_ids': {'eats': str(eats_keys[driver_id])},
                        'orders_provider': {'eda': True, 'taxi': False},
                        'work_status': 'working',
                        'license': {'pd_id': 'license_id'},
                    }
                else:
                    data = {
                        'park_id': park_id,
                        'uuid': driver_id,
                        'orders_provider': {'eda': False, 'taxi': True},
                        'work_status': 'working',
                    }
                profiles.append(
                    {
                        'park_driver_profile_id': park_driver_profile_id,
                        'data': data,
                    },
                )
            return {'profiles': profiles}

    return _mock_driver_profiles_drivers_profiles


@pytest.fixture
def mock_driver_profiles_couriers_updates(mock_driver_profiles):
    def _mock_driver_profiles_couriers_updates(
            binding: typing.Optional[typing.List[dict]] = None,
    ):
        @mock_driver_profiles('/v1/eats-couriers-binding/updates')
        def _(request):
            return {
                'has_next': False,
                'last_known_revision': 'last_known_revision',
                # taxi_id
                # eats_id
                # courier_app == 'taximeter'
                'binding': binding or [],
            }

    return _mock_driver_profiles_couriers_updates


@pytest.fixture
def mock_driver_profiles_couriers_profiles(mock_driver_profiles):
    def _mock_driver_profiles_couriers_profiles(response_by_courier_id: dict):
        profiles = {
            str(courier_id): {
                'park_driver_profile_id': (
                    info['park_id'] + '_' + info['driver_id']
                ),
                'data': {
                    'park_id': info['park_id'],
                    'uuid': info['driver_id'],
                    'work_status': info.get('work_status', 'working'),
                    'orders_provider': {
                        info.get('orders_provider', 'taxi'): True,
                    },
                },
            }
            for courier_id, info in response_by_courier_id.items()
        }

        @mock_driver_profiles('/v1/courier/profiles/retrieve_by_eats_id')
        def _(request):
            eats_courier_id_in_set = request.json['eats_courier_id_in_set']
            return {
                'courier_by_eats_id': [
                    {
                        'eats_courier_id': courier_id,
                        'profiles': (
                            [profiles[courier_id]]
                            if courier_id in profiles
                            else []
                        ),
                    }
                    for courier_id in eats_courier_id_in_set
                ],
            }

    return _mock_driver_profiles_couriers_profiles


def default_park_(park_id):
    return {
        'id': park_id,
        'locale': 'ru',
        'country_id': 'rus',
        'driver_partner_source': 'yandex',
    }


@pytest.fixture
def mock_parks_driver_profiles_search(mock_parks):
    def _mock_driver_profiles_couriers_updates(
            drivers: dict = None,
            parks: dict = None,
            default_park=default_park_,
    ):
        parks = parks if parks else {}

        @mock_parks('/driver-profiles/search')
        def _(request):
            park_ids = sorted(
                request.json['query'].get('park', {}).get('id', []),
            )
            driver_ids = sorted(
                request.json['query'].get('driver', {}).get('id', []),
            )
            if not driver_ids:
                response = {
                    'profiles': [
                        {'park': parks.get(park_id, default_park(park_id))}
                        for park_id in park_ids
                        if default_park
                    ],
                }
            else:
                response = {
                    'profiles': [
                        {'park': {'id': park_id}, 'driver': drivers[driver_id]}
                        for park_id, driver_id in zip(park_ids, driver_ids)
                    ],
                }
            return response

    return _mock_driver_profiles_couriers_updates


@pytest.fixture
def mock_fleet_parks_v1_parks_list(mock_fleet_parks):
    def _mock_parks_v1_parks_list(
            parks: dict = None, default_park=default_park_,
    ):
        parks = parks if parks else {}

        @mock_fleet_parks('/v1/parks/list')
        def _(request):
            park_ids = sorted(
                request.json['query'].get('park', {}).get('ids', []),
            )
            common_fields = {
                'city_id': 'city_id',
                'demo_mode': False,
                'is_active': True,
                'is_billing_enabled': True,
                'is_franchising_enabled': False,
                'login': 'login',
                'name': 'Тест-Курьер ООО',
                'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
            }
            response = {
                'parks': [
                    {
                        **parks.get(park_id, default_park(park_id)),
                        **common_fields,
                    }
                    for park_id in park_ids
                    if default_park or park_id in parks
                ],
            }

            return response

    return _mock_parks_v1_parks_list


def default_driver_tag_(dbid):
    return {'dbid': dbid, 'tags': ['default_tag'], 'uuid': 'default_uuid'}


@pytest.fixture
def mock_tags_match_profile(mock_driver_tags):
    def _mock_tags_match_profile(
            drivers_tags: dict = None, default_driver_tags=default_driver_tag_,
    ):
        drivers_tags = drivers_tags if drivers_tags else {}

        @mock_driver_tags('/v1/drivers/match/profile')
        def _(request):
            driver_id = request.json.get('dbid')

            response = {
                'tags': drivers_tags.get(
                    driver_id, default_driver_tags(driver_id).get('tags'),
                ),
            }

            return response

    return _mock_tags_match_profile


@pytest.fixture
def mock_driver_wall_internal_driver_wall_v1_add(mock_driver_wall):
    def _mock_driver_profiles_couriers_updates():
        @mock_driver_wall('/internal/driver-wall/v1/add')
        def _(request):
            return {'id': request.json['id']}

    return _mock_driver_profiles_couriers_updates


@pytest.fixture
def mock_ya_cc_post(mock_ya_cc):
    def _mock_ya_cc_post(text: str = 'https://ya.cc/t/pwwkT5JaDBUEP'):
        @mock_ya_cc('/--')
        def _(request):
            assert 'test/?' in request.get_data().decode()
            return web.Response(
                text=text,
                headers={'Content-Type': 'text/javascript; charset=utf-8'},
            )

    return _mock_ya_cc_post


@pytest.fixture
def mock_parks_driver_profiles_list_post(mock_parks):
    def _mock_parks_driver_profiles_list_post(
            *,
            city: str = 'Москва',
            country_id: str = 'rus',
            currency: str = 'RUB',
            locale: str = 'ru',
            driver_partner_source: str = 'yandex',
    ):
        @mock_parks('/driver-profiles/list')
        def _(request):
            park_id = request.json['query']['park']['id']
            return {
                'total': 1,
                'offset': 0,
                'driver_profiles': [
                    {
                        'accounts': [{'currency': currency}],
                        'driver_profile': {
                            'driver_license': {
                                'normalized_number': '1111000000',
                            },
                        },
                    },
                ],
                'parks': [
                    {
                        'id': park_id,
                        'city': city,
                        'country_id': country_id,
                        'locale': locale,
                        'provider_config': {'yandex': {'clid': 'clid1'}},
                        'driver_partner_source': driver_partner_source,
                    },
                ],
            }

    return _mock_parks_driver_profiles_list_post


@pytest.fixture
def mock_unique_drivers_retrieve_by_profiles(mockserver):
    def _mock_unique_drivers_retrieve_by_profiles():
        @mockserver.json_handler(
            '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
        )
        async def _(request):
            profile_ids = request.json['profile_id_in_set']
            return {
                'uniques': [
                    {
                        'data': {'unique_driver_id': profile_id},
                        'park_driver_profile_id': profile_id,
                    }
                    for profile_id in profile_ids
                ],
            }

    return _mock_unique_drivers_retrieve_by_profiles


@pytest.fixture
def mock_unique_drivers_retrieve_by_uniques(mockserver):
    def _mock_unique_drivers_retrieve_by_uniques(
            data_by_udid: typing.Dict[str, typing.List[dict]] = None,
    ):
        data_by_udid = data_by_udid or {}

        @mockserver.json_handler(
            '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
        )
        async def _(request):
            udids = request.json['id_in_set']
            profiles = []
            for udid in udids:
                if udid in data_by_udid:
                    profiles.append(
                        {'unique_driver_id': udid, 'data': data_by_udid[udid]},
                    )
                else:
                    park_id, driver_id = udid.split('_')
                    profiles.append(
                        {
                            'unique_driver_id': udid,
                            'data': [
                                {
                                    'park_id': park_id,
                                    'driver_profile_id': driver_id,
                                    'park_driver_profile_id': udid,
                                },
                            ],
                        },
                    )
            return {'profiles': profiles}

    return _mock_unique_drivers_retrieve_by_uniques


@pytest.fixture(autouse=True)
def _default_external_mock(
        mock_driver_profiles_drivers_profiles,
        mock_driver_profiles_couriers_updates,
        mock_driver_profiles_couriers_profiles,
        mock_parks_driver_profiles_search,
        mock_fleet_parks_v1_parks_list,
        mock_driver_wall_internal_driver_wall_v1_add,
        mock_ya_cc_post,
        mock_parks_driver_profiles_list_post,
        mock_unique_drivers_retrieve_by_profiles,
        mock_unique_drivers_retrieve_by_uniques,
        mock_tags_match_profile,
        mock_hiring_candidates_py3_leads_list,
):
    mock_driver_profiles_drivers_profiles(eats_keys={})
    mock_driver_profiles_couriers_updates([])
    mock_driver_profiles_couriers_profiles({})
    mock_parks_driver_profiles_search()
    mock_fleet_parks_v1_parks_list()
    mock_driver_wall_internal_driver_wall_v1_add()
    mock_ya_cc_post()
    mock_parks_driver_profiles_list_post()
    mock_unique_drivers_retrieve_by_profiles()
    mock_unique_drivers_retrieve_by_uniques()
    mock_tags_match_profile()
    mock_hiring_candidates_py3_leads_list(special_status={})


class TablesDiffCounts:
    DEFAULT_DIFF_TABLES = {
        'daily_stats': 0,
        'referral_profiles': 0,
        'synced_orders': 0,
        'rules': 0,
        'tasks': 0,
        'payment_id_to_referral_id': 0,
        'couriers': 0,
        'duplicates_history': 0,
        'notifications': 0,
        'cache_referral_profiles': 0,
    }

    def __init__(self, context, diff_tables: typing.Dict[str, int] = None):
        self.context = context
        default_diff_tables = dict(self.DEFAULT_DIFF_TABLES)
        if diff_tables:
            default_diff_tables.update(diff_tables)
        self.diff_tables = default_diff_tables
        self.start_diff: typing.Dict[str, int] = {}

    async def __aenter__(self):
        for table_name in self.diff_tables:
            self.start_diff[table_name] = await self.count_table(table_name)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        for table_name, hypothesis_count in self.diff_tables.items():
            start_count = self.start_diff[table_name]
            finish_count = await self.count_table(table_name)
            diff = finish_count - start_count
            assert (
                hypothesis_count == diff
            ), f'Incorrect diff table {table_name}'

    async def count_table(self, table_name: str):
        async with self.context.pg.master_pool.acquire() as connection:
            return await connection.fetchval(
                f'SELECT count(*) FROM {table_name}',
            )


@pytest.fixture
def mock_get_query_positions(mock_driver_trackstory):
    def mock_get_query_positions_helper(
            driver_positions: typing.Mapping[str, typing.List[dict]],
            default_positions: typing.Optional[typing.List[dict]] = None,
    ):
        @mock_driver_trackstory('/query/positions')
        async def _query_positions(request):
            result = []
            for driver_id in request.json['driver_ids']:
                if driver_id in driver_positions:
                    result.extend(driver_positions[driver_id])
            if not result and default_positions:
                result.extend(default_positions)
            return {'results': [result]}

    return mock_get_query_positions_helper


@pytest.fixture
def mock_get_query_positions_default(mock_get_query_positions):
    mock_get_query_positions(
        {},
        default_positions=[
            {
                'source': 'Raw',
                'position': {
                    'lat': 55.75222,
                    'lon': 37.61556,
                    'timestamp': int(dt.datetime.timestamp(dt.datetime.now())),
                },
            },
            {
                'source': 'Adjusted',
                'position': {
                    'lat': 55.76103,
                    'lon': 37.62017,
                    'timestamp': int(dt.datetime.timestamp(dt.datetime.now())),
                },
            },
        ],
    )


@pytest.fixture
def mock_get_nearest_zone(mock_superapp_misc):
    def _make_result(zone: typing.Optional[str] = None) -> dict:
        return {
            'services': [
                {
                    'service': 'taxi',
                    'status': 'found',
                    'payload': {'nearest_zone': zone},
                }
                if zone
                else {
                    'service': 'taxi',
                    'status': 'not_found',
                    'payload': {
                        'message': 'The driver is outside the tariff zone',
                    },
                },
            ],
        }

    def _wrap(
            zones: typing.Mapping[
                str, typing.Iterable[typing.Tuple[float, float]],
            ],
            default_zone: typing.Optional[str] = None,
    ):
        @mock_superapp_misc('/4.0/mlutp/v1/nearest_zone')
        async def _nearest_zone(request) -> dict:
            position_to_look_for = pytest.approx(
                request.json['position'], abs=0.0000001,
            )
            for zone, positions in zones.items():
                if any(
                        position == position_to_look_for
                        for position in positions
                ):
                    return _make_result(zone)
            return _make_result(default_zone)

    return _wrap


@pytest.fixture
def mock_fail_to_get_nearest_zone(mock_get_nearest_zone):
    mock_get_nearest_zone({})


@pytest.fixture
def mock_driver_zones(mock_get_query_positions, mock_get_nearest_zone):
    def mock_driver_zones_helper(
            driver_zones: typing.Dict[str, str],
            default_zone: typing.Optional[str] = None,
    ):
        driver_positions = {}
        position_zones: typing.Dict[
            str, typing.List[typing.Tuple[float, float]],
        ] = {}
        for index, (driver_id, zone) in enumerate(driver_zones.items()):
            driver_positions[driver_id] = [
                {
                    'source': 'Raw',
                    'position': {
                        'lat': index,
                        'lon': index,
                        'timestamp': int(
                            dt.datetime.timestamp(dt.datetime.now()),
                        ),
                    },
                },
            ]
            position_zones.setdefault(zone, [])
            position_zones[zone].append((index, index))
        mock_get_query_positions(
            driver_positions,
            default_positions=[
                {
                    'source': 'Raw',
                    'position': {
                        'lat': -1,
                        'lon': -1,
                        'timestamp': int(
                            dt.datetime.timestamp(dt.datetime.now()),
                        ),
                    },
                },
            ],
        )
        mock_get_nearest_zone(position_zones, default_zone=default_zone)

    return mock_driver_zones_helper


@pytest.fixture
def mock_promocode_response(mockserver):
    class PromocodeResponseContext:
        def __init__(self):
            self.is_promocode_created = None
            self.expected_series = None

        def set_response_settings(
                self, is_promocode_created: bool, expected_series: str,
        ):
            self.is_promocode_created = is_promocode_created
            self.expected_series = expected_series

    context = PromocodeResponseContext()

    @mockserver.json_handler('/driver-promocodes/internal/v1/promocodes')
    def response(request):  # pylint: disable=unused-variable
        series_name = request.json['series_name']
        if context.expected_series:
            assert series_name in context.expected_series

        if context.is_promocode_created:
            return mockserver.make_response(
                status=200,
                json={
                    'id': 'promocode1',
                    'code': 'test',
                    'antifraud_resolutions': ['test'],
                    'country': 'test',
                    'status': 'activated',
                    'is_seen': False,
                    'used_for_orders': [],
                    'is_created_by_service': True,
                    'created_at': dt.datetime.now().isoformat(),
                    'created_by': 'test',
                    'updated_at': dt.datetime.now().isoformat(),
                    'type': 'commission',
                    'title_key': 'test',
                    'description_key': 'test',
                    'is_support_series': False,
                    'entity_id': 'p1_d1',
                    'entity_type': 'park_driver_profile_id',
                    'series_name': 'test',
                },
            )
        return mockserver.make_response(
            status=400,
            json={
                'id': 'promocode1',
                'code': 'test',
                'message': 'test',
                'antifraud_resolutions': ['test'],
            },
        )

    return context


@pytest.fixture
def mock_hiring_candidates_py3_leads_list(mock_hiring_candidates_py3):
    def _mock_hiring_candidates_py3_leads_list(
            special_status: typing.Dict[str, bool],
    ):
        @mock_hiring_candidates_py3('/v1/leads/list')
        def _handler(request):
            return {
                'leads': [
                    {
                        'lead_id': 'lead_id',
                        'fields': [
                            {
                                'name': 'activator_check',
                                'value': special_status.get(
                                    request.json['personal_license_id', True],
                                ),
                            },
                        ],
                    },
                ],
            }

    return _mock_hiring_candidates_py3_leads_list
