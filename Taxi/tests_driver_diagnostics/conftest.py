# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=dangerous-default-value
import json

import pytest

from driver_diagnostics_plugins import *  # noqa: F403 F401

from tests_driver_diagnostics import utils

DEFAULT_DP_BLOCKLISTS = {
    'DriverCarBlacklistedTemp': {
        'message': (
            'Машина временно отключена от заказов. Причина: car block. '
            'Блокировка снимется через 3 дней'
        ),
        'till': '2020-01-02T20:10:00.0+0000',
        'title': 'Доступ приостановлен',
    },
    'DriverLicenseBlacklisted': {
        'message': (
            'Ваша лицензия в чёрном списке. Обратитесь в службу поддержки.'
        ),
        'title': 'Доступ запрещен',
    },
}

DEFAULT_DP_REASONS = {
    'ParkAggregatorDebt': ['limit: -100.000000, balance: -200.000000'],
}


def _error_response(mockserver, error_message, status=400):
    return mockserver.make_response(
        json={'code': str(status), 'message': error_message}, status=status,
    )


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))


class DriverProtocolContext:
    def __init__(self):
        self.reasons = {}
        self.blocklists = {}

    def set_driver_blocks(
            self, reasons=DEFAULT_DP_REASONS, blocklists=DEFAULT_DP_BLOCKLISTS,
    ):
        self.reasons = reasons
        self.blocklists = blocklists


@pytest.fixture(name='driver_protocol', autouse=True)
def driver_protocol(mockserver):
    context = DriverProtocolContext()

    @mockserver.json_handler('/driver-protocol/service/driver/blocks')
    def _service_driver_blocks(request):
        return mockserver.make_response(
            json={
                'can_take_orders': not (
                    bool(context.reasons) and bool(context.blocklists)
                ),
                'reasons': context.reasons,
                'blocklist_reasons': context.blocklists,
            },
            status=200,
        )

    return context


class CandidatesContext:
    def __init__(self):
        self.reasons = {}
        self.details = {}
        self.driver_id = 'driver_id1'
        self.error = False

    def set_response_reasons(self, reasons, details, driver_id='driver_id1'):
        self.reasons = reasons
        self.details = details
        self.driver_id = driver_id

    def set_error(self):
        self.error = True


@pytest.fixture(name='candidates', autouse=True)
def mock_candidates(mockserver):
    context = CandidatesContext()

    @mockserver.json_handler('/candidates/satisfy')
    def _satisfy(request):
        if context.error:
            return _error_response(mockserver, 'error', 500)
        return {
            'drivers': [
                {
                    'dbid': 'park_id1',
                    'uuid': context.driver_id,
                    'reasons': context.reasons,
                    'details': context.details,
                    'is_satisfied': False,
                },
            ],
        }

    return context


class DriverProfilesContext:
    def __init__(self):
        self.contractor_data = {}
        self.error_code = 500

    def set_contractor_data(
            self,
            park_contractor_profile_id,
            vehicle_id='1234',
            orders_provider={'taxi': True},
            providers=['yandex'],
            external_ids: dict = None,
    ):
        data = {}
        if vehicle_id:
            data['car_id'] = vehicle_id
        if orders_provider:
            data['orders_provider'] = orders_provider
        if providers:
            data['providers'] = providers
        if external_ids:
            data['external_ids'] = external_ids

        self.contractor_data[park_contractor_profile_id] = data

    def set_error(self, code):
        self.error_code = code


@pytest.fixture(name='driver_profiles', autouse=True)
def mock_driver_profiles(mockserver):
    context = DriverProfilesContext()
    context.set_contractor_data(utils.PARK_CONTRACTOR_PROFILE_ID)

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles_retrieve(request):
        park_contractor_profile_id = request.json['id_in_set'][0]
        if park_contractor_profile_id in context.contractor_data:
            body = {
                'profiles': [
                    {
                        'park_driver_profile_id': park_contractor_profile_id,
                        'data': context.contractor_data[
                            park_contractor_profile_id
                        ],
                    },
                ],
            }
            if context.contractor_data[park_contractor_profile_id] is None:
                body['profiles'][0]['data'] = {}
            return mockserver.make_response(
                response=json.dumps(body), status=200,
            )
        return _error_response(mockserver, 'error', context.error_code)

    return context


class QCContext:
    def __init__(self):
        self.exams = {}
        self.error_code = 500

    def set_exams(self, car_id, exams):
        self.exams[car_id] = exams

    def set_error(self, code):
        self.error_code = code


@pytest.fixture(name='qc_cpp', autouse=True)
def mock_qc_cpp(mockserver):
    context = QCContext()

    @mockserver.json_handler('/quality-control-cpp/api/v1/state')
    def _state(request):
        car_id = request.query['id']
        if car_id in context.exams:
            body = {
                'type': 'car',
                'id': 'park_id1_driver_id1',
                'exams': context.exams[car_id],
            }
            return mockserver.make_response(
                response=json.dumps(body), status=200,
            )
        return _error_response(mockserver, 'error', context.error_code)

    return context


class DriverCategoriesApiContext:
    def __init__(self):
        self.categories = ['econom']
        self.calls = 0

    def set_categories(self, categories):
        self.categories = categories

    def has_calls(self):
        return bool(self.calls)


@pytest.fixture(name='driver_categories_api', autouse=True)
def mock_driver_categories_api(mockserver):
    context = DriverCategoriesApiContext()

    @mockserver.json_handler(
        '/driver-categories-api/internal/v2/allowed_driver_categories',
    )
    def _satisfy(request):
        context.calls += 1
        return {'categories': context.categories}

    return context


class BlocklistContext:
    def __init__(self):
        self.blocks = {}
        self.calls = 0

    def set_block(self, block_id, data):
        self.blocks[block_id] = data

    def set_blocks(self, blocks):
        self.blocks = blocks

    def has_calls(self):
        return bool(self.calls)


@pytest.fixture(name='blocklist', autouse=True)
def mock_blocklist(mockserver):
    context = BlocklistContext()

    @mockserver.json_handler('/blocklist/internal/blocklist/v1/reason')
    def _get_reason(request):
        context.calls += 1
        return {'reasons': context.blocks}

    return context


@pytest.fixture(name='driver_trackstory', autouse=True)
def mock_driver_trackstory(mockserver, load_json):
    @mockserver.json_handler('/driver-trackstory/query/positions')
    def _query_positions(request):
        response_dict = load_json('driver_trackstory.json')
        driver_id = request.json['driver_ids'][0]
        if driver_id in response_dict:
            item = {
                'position': {
                    'direction': 36,
                    'speed': 2.243076218814374,
                    'timestamp': 1600861713,
                },
                'source': 'Adjusted',
            }
            item['position']['lat'] = response_dict[driver_id]['lat']
            item['position']['lon'] = response_dict[driver_id]['lon']
            return mockserver.make_response(
                json={'results': [[item]]}, status=200,
            )
        return _error_response(mockserver, 'Driver not found', 404)


class EatsCoreContext:
    def __init__(self):
        self.work_status = 'active'
        self.fns_step = None
        self.billing_status = None
        self.courier_external_id = None

    def set_context(
            self,
            work_status=None,
            fns_step=None,
            billing_status=None,
            courier_external_id=None,
    ):
        self.work_status = work_status if work_status else 'active'
        self.fns_step = fns_step
        self.billing_status = billing_status
        self.courier_external_id = courier_external_id


@pytest.fixture(name='eats_core_context')
def _eats_core_context():
    return EatsCoreContext()


@pytest.fixture(name='mock_eats_core')
def _mock_eats_core(mockserver, eats_core_context):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/', prefix=True,
    )
    def _mock_couriers(request):
        return utils.get_courier(
            eats_core_context.work_status,
            external_id=eats_core_context.courier_external_id,
        )

    @mockserver.json_handler(
        '/eats-core-courier-check/internal-api/v1/courier/fns/check',
    )
    def _mock_fns(request):
        return {'status': 'success', 'step': eats_core_context.fns_step}

    @mockserver.json_handler(
        '/eats-core-courier-check/internal-api/v1/courier/billing/check',
    )
    def _mock_billing(request):
        return {'status': eats_core_context.billing_status}


class HiringCandidatesContext:
    def __init__(self):
        self.x_consumer_id = ''
        self.external_ids = None
        self.fields = []

    def set_context(self, x_consumer_id='', external_ids=None, fields=[]):
        self.x_consumer_id = x_consumer_id
        self.external_ids = external_ids
        self.fields = fields


@pytest.fixture(name='hiring_candidates_context')
def _hiring_candidates_context():
    return HiringCandidatesContext()


@pytest.fixture(name='mock_hiring_candidates')
def _mock_hiring_candidates(mockserver, hiring_candidates_context):
    @mockserver.json_handler('/logistic-hiring-candidates/v1/leads/list')
    def _mock_leads(request):
        assert (
            request.headers['x-consumer-id']
            == hiring_candidates_context.x_consumer_id
        )
        return {
            'leads': [
                {
                    'lead_id': request.json['lead_ids'][0],
                    'fields': hiring_candidates_context.fields,
                },
            ],
            'is_bounded_by_limit': False,
        }


class DriverLessonsContext:
    def __init__(self):
        self.lessons_progress = []

    def set_context(self, lessons_progress):
        self.lessons_progress = lessons_progress

    def add_lesson_progress(self, lesson_id, progress, driver_id, park_id):
        self.lessons_progress.append(
            {
                'lesson_id': lesson_id,
                'progress': progress,
                'driver_id': driver_id,
                'park_id': park_id,
            },
        )


@pytest.fixture(name='driver_lessons_context')
def _driver_lessons_context():
    return DriverLessonsContext()


@pytest.fixture(name='mock_driver_lessons')
def _mock_driver_lessons(mockserver, driver_lessons_context):
    @mockserver.json_handler(
        '/driver-lessons/internal'
        '/driver-lessons/v1/lessons-progress'
        '/bulk-retrieve',
    )
    def _mock_training_status(request):
        def is_this_driver_lesson(lesson, request):
            driver = request.json['drivers'][0]
            return (
                lesson['driver_id'] == driver['driver_id']
                and lesson['park_id'] == driver['park_id']
            )

        try:
            return {
                'lessons_progress': [
                    next(
                        x
                        for x in driver_lessons_context.lessons_progress
                        if is_this_driver_lesson(x, request)
                    ),
                ],
            }
        except StopIteration:
            return {'lessons_progress': []}


class FleetParksContext:
    def __init__(self):
        self.parks = {}

    def set_parks(self, parks):
        self.parks = parks


@pytest.fixture(name='fleet_parks')
def fleet_parks(mockserver):
    context = FleetParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_retrieve_park_list(request):
        result = []
        for i in request.json['query']['park']['ids']:
            result.append(context.parks[i])
        return {'parks': result}

    return context
