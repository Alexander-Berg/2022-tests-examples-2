import collections
import copy
import datetime
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import asynctest
import pytest

from client_order_core import helper as order_core_helper
from taxi.clients import experiments3

from taxi_safety_center import exceptions
from taxi_safety_center.generated.service.swagger.models import api
from taxi_safety_center.logic import pushes as push_logic
from test_taxi_safety_center import data_generators


ACCIDENTS_HANDLE_PATH = '/v1/accidents'

SELECT_ACCIDENT_QUERY = (
    'SELECT * from safety_center.accidents WHERE idempotency_key=\'{}\'::TEXT'
)

# table schema for cursor rows in python
ACCIDENT_TABLE_SCHEMA = collections.OrderedDict(
    [
        ('accident_id', str),
        ('idempotency_key', str),
        ('order_id', str),
        ('order_alias_id', str),
        ('user_id', str),
        ('yandex_uid', str),
        ('confidence', int),
        ('occurred_at', datetime.datetime),
        ('created_at', datetime.datetime),
        ('updated_at', datetime.datetime),
        ('confirmed', bool),
    ],
)
DEFAULT_USER = '9876'
DEFAULT_CONFIDENCE = data_generators.DEFAULT_CONFIDENCE  # 30
DEFAULT_CONFIDENCE_THRESHOLD = DEFAULT_CONFIDENCE + 5
CONFIDENCE_DELTA = DEFAULT_CONFIDENCE_THRESHOLD - DEFAULT_CONFIDENCE  # 5
PUSH_TRANSLATION_KEY = 'safety_center.pushes.accidents.msg'
PUSH_TRANSLATIONS = {
    PUSH_TRANSLATION_KEY: {
        'ru': 'Нам кажется что случилось ДТП. С вами всё в порядке?',
    },
}

DEFAULT_ACCIDENTS_CONFIG = {
    'accident': {
        'confidence_threshold': DEFAULT_CONFIDENCE_THRESHOLD,
        'msg': PUSH_TRANSLATION_KEY,
        'ttl': 100500,
        'intent': 'safety_center_accident',
        'experiments': [],
        'enabled': True,
    },
}

DEFAULT_ARCHIVE_RESPONSE = {
    'user_id': 'user_id1',
    'user_uid': 'user_uid1',
    'user_locale': 'ru',
}


class PostTestScenario:
    def __init__(
            self,
            scenario_type: str,  # insert, update, insert-get, update-get
            # 'get' postfix doesn't affect verification
            # it is only for code readability purposes
            awaited_status: int,  # 200/404
            accident: api.NewAccidentObject,
            patches: Optional[
                List[Dict[str, Any]]
            ] = None,  # pylint: disable=bad-whitespace
            error_code: Optional[str] = None,
            user_id: Optional[str] = None,
    ):
        self.scenario_type = scenario_type
        self.awaited_status = awaited_status
        if patches is None:
            self.accident = accident
        else:
            for patch in patches:
                self.accident = self.patch_accident(accident, patch)
        self.error_code = error_code
        self.user_id = user_id

    async def verify_response(self, response, pgsql):
        assert response.status == self.awaited_status
        if self.awaited_status == 200:
            accident_id = (await response.json())['accident_id']
            if 'insert' in self.scenario_type:
                assert accident_id
                self.accident.accident_id = accident_id
            else:
                assert self.accident.accident_id == accident_id

            cursor = pgsql['safety_center'].cursor()
            cursor.execute(
                SELECT_ACCIDENT_QUERY.format(self.accident.idempotency_key),
            )

            # cursor is a generator, so I unpack it with list comprehension
            result = [row for row in cursor]
            assert cursor.rowcount == 1
            self._compare_row(result[0])
        else:  # 404
            response = await response.json()
            assert self.error_code == response['code']
            if (
                    self.error_code
                    == exceptions.IdempotencyKeyDuplicate.error_code
            ):
                assert (
                    response['details']['idempotency_key']
                    == self.accident.idempotency_key
                )

    def _compare_row(self, row):
        for (column_key, column_type), row_value in zip(
                ACCIDENT_TABLE_SCHEMA.items(), row,
        ):

            if issubclass(datetime.datetime, column_type):
                # it should be 'if column_type is datetime.datetime:'...
                # but when running pytest, datetime.datetime call in runtime
                # returns <class 'freezegun.api.FakeDatetime'>
                # and condition
                # 'if datetime.datetime is freezegun.api.FakeDateTime'
                # is always false

                # I don't want to compare datetime values so compare only type
                assert isinstance(row_value, column_type)
                return
            if column_key == 'order_id':
                return  # dont test it here
            assert row_value == getattr(self.accident, column_key, None)

    @staticmethod
    def patch_accident(accident, patch):
        accident_dict = accident.serialize()
        result = accident_dict.copy()
        for key, value in patch.items():
            result[key] = value
        return api.NewAccidentObject.deserialize(result)


@pytest.mark.pgsql('safety_center')
@pytest.mark.config(SAFETY_CENTER_PUSH_SETTINGS=DEFAULT_ACCIDENTS_CONFIG)
@pytest.mark.parametrize(
    'scenario',
    [
        PostTestScenario(
            scenario_type='insert',
            awaited_status=200,
            accident=data_generators.generated_accident(1),
        ),
        PostTestScenario(
            scenario_type='insert',
            awaited_status=404,
            accident=data_generators.generated_accident(1),
            patches=[{'order_alias_id': 'missing_alias_id'}],
            error_code='no_order_for_alias_id',
        ),
    ],
)
@pytest.mark.translations(client_messages=PUSH_TRANSLATIONS)
# This test is not idempotent, can be run only once.
# @order_core_helper.ORDER_CORE_ENABLED
async def test_post_accident_insert(
        pgsql,
        web_app_client,
        mock_archive_response,
        scenario,
        order_core_mock,
):
    mock_archive_response(DEFAULT_ARCHIVE_RESPONSE)
    response = await web_app_client.post(
        ACCIDENTS_HANDLE_PATH, data=json.dumps(scenario.accident.serialize()),
    )
    await scenario.verify_response(response, pgsql)


@pytest.mark.pgsql(
    'safety_center', queries=[data_generators.insert_accident_query(1)],
)
@pytest.mark.config(SAFETY_CENTER_PUSH_SETTINGS=DEFAULT_ACCIDENTS_CONFIG)
@pytest.mark.parametrize(
    'scenario',
    [
        PostTestScenario(
            scenario_type='update',
            awaited_status=200,
            accident=data_generators.generated_accident(1, generate_id=True),
            patches=[data_generators.generated_accident_dict(2)],
        ),
    ],
)
@order_core_helper.ORDER_CORE_ENABLED
async def test_post_accident_update(
        pgsql, web_app_client, scenario, order_core_mock,
):
    response = await web_app_client.post(
        ACCIDENTS_HANDLE_PATH, data=json.dumps(scenario.accident.serialize()),
    )
    await scenario.verify_response(response, pgsql)


@pytest.mark.pgsql(
    'safety_center', queries=[data_generators.insert_accident_query(1)],
)
@pytest.mark.config(SAFETY_CENTER_PUSH_SETTINGS=DEFAULT_ACCIDENTS_CONFIG)
@pytest.mark.parametrize(
    'scenario',
    [
        PostTestScenario(
            scenario_type='insert-get',
            awaited_status=200,
            accident=data_generators.generated_accident(1, generate_id=False),
        ),
        PostTestScenario(
            scenario_type='update-get',
            awaited_status=200,
            accident=data_generators.generated_accident(1, generate_id=True),
        ),
    ],
)
@pytest.mark.translations(client_messages=PUSH_TRANSLATIONS)
@order_core_helper.ORDER_CORE_ENABLED
async def test_post_accident_get(
        pgsql,
        web_app_client,
        mock_archive_response,
        scenario,
        monkeypatch,
        mock,
        order_core_mock,
):
    """scenario that takes place on IdempotencyKeyDuplicate"""
    mock_archive_response(DEFAULT_ARCHIVE_RESPONSE)
    response = await web_app_client.post(
        ACCIDENTS_HANDLE_PATH, data=json.dumps(scenario.accident.serialize()),
    )
    await scenario.verify_response(response, pgsql)


@pytest.mark.pgsql('safety_center')
@pytest.mark.config(SAFETY_CENTER_PUSH_SETTINGS=DEFAULT_ACCIDENTS_CONFIG)
@pytest.mark.parametrize(
    'scenario',
    [
        PostTestScenario(
            scenario_type='update',
            awaited_status=404,
            accident=data_generators.generated_accident(1, generate_id=True),
            error_code='not_found_error',
        ),
    ],
)
async def test_post_accident_update_missing_id(
        pgsql, web_app_client, scenario,
):
    response = await web_app_client.post(
        ACCIDENTS_HANDLE_PATH, data=json.dumps(scenario.accident.serialize()),
    )
    await scenario.verify_response(response, pgsql)


@pytest.mark.pgsql(
    'safety_center',
    queries=[
        data_generators.insert_accident_query(0),
        data_generators.insert_accident_query(
            CONFIDENCE_DELTA,
        ),  # to ensure that push was already sent
    ],
)
@pytest.mark.parametrize(
    'scenario',
    [
        PostTestScenario(
            scenario_type='insert',
            awaited_status=200,
            accident=data_generators.generated_accident(1, generate_id=False),
            user_id='user_id1',
        ),
        PostTestScenario(
            scenario_type='update',
            awaited_status=200,
            accident=data_generators.generated_accident(0, generate_id=True),
            patches=[data_generators.generated_accident_dict(3)],
            user_id='user_id1',
        ),
        PostTestScenario(
            scenario_type='update',
            awaited_status=200,
            accident=data_generators.generated_accident(
                CONFIDENCE_DELTA, generate_id=True,
            ),
            patches=[
                data_generators.generated_accident_dict(CONFIDENCE_DELTA + 1),
            ],
            user_id='user_id1',
        ),
    ],
)
@pytest.mark.parametrize(
    'accident_patch,confidence_need_send_push',
    [
        ({'confidence': DEFAULT_CONFIDENCE}, False),
        ({'confidence': DEFAULT_CONFIDENCE_THRESHOLD}, True),
        ({'confidence': DEFAULT_CONFIDENCE_THRESHOLD + 10}, True),
    ],
)
@pytest.mark.parametrize(
    'user_experiments,experiment_need_send_push',
    [
        (['send_push_experiment'], True),
        (['wrong_experiment'], False),
        ([], False),
    ],
)
@pytest.mark.parametrize(
    ['nearest_zone', 'country_need_send_push'],
    [('Москва', True), ('Балашиха', False)],
)
@pytest.mark.config(
    SAFETY_CENTER_PUSH_SETTINGS={
        'accident': {
            'confidence_threshold': DEFAULT_CONFIDENCE_THRESHOLD,
            'msg': PUSH_TRANSLATION_KEY,
            'ttl': 100500,
            'intent': 'safety_center_accident',
            'experiments': ['send_push_experiment'],
            'enabled': True,
            'countries': ['rus'],
        },
    },
)
@pytest.mark.translations(client_messages=PUSH_TRANSLATIONS)
@order_core_helper.ORDER_CORE_ENABLED
async def test_post_accident_push(
        pgsql,
        web_app_client,
        scenario,
        accident_patch,
        confidence_need_send_push,
        user_experiments,
        experiment_need_send_push,
        nearest_zone,
        country_need_send_push,
        mock_archive_response,
        mock_experiments_response,
        order_core_mock,
):
    # deepcopy to avoid changing parametrize arguments before 2nd usage
    scenario = copy.deepcopy(scenario)
    is_confidence_delta_scenario = scenario.accident.accident_id == (
        'accident-id-' + str(CONFIDENCE_DELTA)
    )
    if not is_confidence_delta_scenario:
        scenario.accident = scenario.patch_accident(
            scenario.accident, accident_patch,
        )
    archive_response = copy.deepcopy(DEFAULT_ARCHIVE_RESPONSE)
    archive_response['nz'] = nearest_zone
    mock_archive_response(archive_response)
    mock_experiments_response(user_experiments)
    with asynctest.patch.object(push_logic, 'send_push') as patched:
        response = await web_app_client.post(
            ACCIDENTS_HANDLE_PATH,
            data=json.dumps(scenario.accident.serialize()),
        )
        await scenario.verify_response(response, pgsql)
        if all(
                [
                    confidence_need_send_push,
                    experiment_need_send_push,
                    country_need_send_push,
                    not is_confidence_delta_scenario,
                ],
        ):
            patched.assert_awaited_once()
        else:
            patched.assert_not_awaited()


@pytest.mark.parametrize(
    'scenario',
    [
        PostTestScenario(
            scenario_type='insert',
            awaited_status=200,
            accident=data_generators.generated_accident(1, generate_id=False),
            user_id='user_id1',
        ),
    ],
)
@pytest.mark.config(
    SAFETY_CENTER_PUSH_SETTINGS={
        'accident': {
            'confidence_threshold': DEFAULT_CONFIDENCE + 4,
            'msg': PUSH_TRANSLATION_KEY,
            'ttl': 100500,
            'intent': 'safety_center.accident',
            'experiments': [],
            'enabled': False,
        },
    },
)
@order_core_helper.ORDER_CORE_ENABLED
async def test_post_accident_push_not_sent(
        pgsql,
        web_app_client,
        scenario,
        mock_archive_response,
        mock_experiments_response,
        order_core_mock,
):
    # deepcopy to avoid changing parametrize arguments before 2nd usage
    scenario = copy.deepcopy(scenario)
    mock_archive_response(DEFAULT_ARCHIVE_RESPONSE)
    with asynctest.patch.object(push_logic, 'send_push') as patched:
        response = await web_app_client.post(
            ACCIDENTS_HANDLE_PATH,
            data=json.dumps(scenario.accident.serialize()),
        )
        await scenario.verify_response(response, pgsql)
        patched.assert_not_awaited()


@pytest.mark.pgsql(
    'safety_center', queries=[data_generators.insert_accident_query(1)],
)
@pytest.mark.parametrize(
    'scenario',
    [
        PostTestScenario(
            scenario_type='update',
            awaited_status=409,
            error_code='confidence_decrease',
            accident=data_generators.generated_accident(1, generate_id=True),
            patches=[
                data_generators.generated_accident_dict(2),
                {'confidence': DEFAULT_CONFIDENCE - 20},
            ],
            user_id='user_id1',
        ),
    ],
)
@pytest.mark.translations(client_messages=PUSH_TRANSLATIONS)
@pytest.mark.config(SAFETY_CENTER_PUSH_SETTINGS=DEFAULT_ACCIDENTS_CONFIG)
async def test_post_accident_confidence_decrease(
        pgsql, web_app_client, scenario, mock_archive_response,
):
    mock_archive_response(DEFAULT_ARCHIVE_RESPONSE)

    with asynctest.patch.object(push_logic, 'send_push') as patched:
        response = await web_app_client.post(
            ACCIDENTS_HANDLE_PATH,
            data=json.dumps(scenario.accident.serialize()),
        )
        await scenario.verify_response(response, pgsql)
        patched.assert_not_awaited()


@pytest.mark.config(
    SAFETY_CENTER_PUSH_SETTINGS={
        'accident': {
            'confidence_threshold': 1,
            'msg': PUSH_TRANSLATION_KEY,
            'ttl': 100500,
            'intent': 'safety_center_accident',
            'experiments': ['send_push_experiment'],
            'enabled': True,
            'countries': ['rus'],
        },
    },
)
@pytest.mark.translations(client_messages=PUSH_TRANSLATIONS)
@pytest.mark.pgsql(
    'safety_center', queries=[data_generators.insert_accident_query(1, 0)],
)
@pytest.mark.parametrize(
    'is_existing_accident',
    (pytest.param(False, id='insert'), pytest.param(True, id='update')),
)
@pytest.mark.parametrize(
    ('idempotency_key', 'experiment_tariff', 'is_push_expected'),
    (
        pytest.param('0', 'econom', True, id='push_for_tariff_match'),
        pytest.param('1', 'cargo', False, id='no_push_for_tariff_mismatch'),
    ),
)
@order_core_helper.ORDER_CORE_ENABLED
async def test_push_tariff_check(
        web_app_client,
        mock_archive_response,
        monkeypatch,
        order_core_mock,
        is_existing_accident,
        idempotency_key,
        experiment_tariff,
        is_push_expected,
):
    archive_response = copy.deepcopy(DEFAULT_ARCHIVE_RESPONSE)
    archive_response['nz'] = 'Москва'
    mock_archive_response(archive_response)

    async def get_values_patch(
            *args,
            experiments_args: List[experiments3.ExperimentsArg],
            **kwargs,
    ):
        assert experiments_args == [
            experiments3.ExperimentsArg(
                name='user_id', type='string', value='user_id1',
            ),
            experiments3.ExperimentsArg(
                name='tariff', type='string', value='econom',
            ),
        ]
        if experiments_args[1].value == experiment_tariff:
            return [
                experiments3.ExperimentsValue(
                    name='send_push_experiment', value=None,
                ),
            ]
        return []

    monkeypatch.setattr(
        experiments3.Experiments3Client, 'get_values', get_values_patch,
    )

    with asynctest.patch.object(push_logic, 'send_push') as patched:
        request_accident = data_generators.generated_accident(
            1, generate_id=is_existing_accident,
        )
        request_accident.idempotency_key = idempotency_key
        response = await web_app_client.post(
            ACCIDENTS_HANDLE_PATH,
            data=json.dumps(request_accident.serialize()),
        )
        assert response.status == 200

        if is_push_expected:
            patched.assert_awaited_once()
        else:
            patched.assert_not_awaited()


@pytest.mark.parametrize(
    'is_tariff_disabled',
    [
        pytest.param(
            True,
            marks=(
                pytest.mark.config(
                    SAFETY_CENTER_CHATTERBOX_TICKET_SETTINGS=dict(
                        threshold=60,
                        macros_ids=[0],
                        countries=['rus'],
                        disabled_tariffs=['econom'],
                    ),
                ),
            ),
        ),
        pytest.param(False),
    ],
)
@pytest.mark.pgsql('safety_center')
@pytest.mark.config(
    SAFETY_CENTER_PUSH_SETTINGS={
        'accident': {
            'confidence_threshold': DEFAULT_CONFIDENCE_THRESHOLD,
            'msg': PUSH_TRANSLATION_KEY,
            'ttl': 100500,
            'intent': 'safety_center_accident',
            'enabled': True,
            'countries': ['rus'],
        },
    },
    SAFETY_CENTER_CREATE_CHATTERBOX_TICKET_ENABLED=True,
    SAFETY_CENTER_CHATTERBOX_TICKET_SETTINGS=dict(
        threshold=60, macros_ids=[0], countries=['rus'], disabled_tariffs=[],
    ),
)
@pytest.mark.translations(client_messages=PUSH_TRANSLATIONS)
@pytest.mark.parametrize(
    [
        'confidence',
        'confidence_need_create_ticket',
        'confidence_need_send_push',
    ],
    [
        (DEFAULT_CONFIDENCE, False, False),
        (65, True, True),
        (DEFAULT_CONFIDENCE_THRESHOLD, False, True),
    ],
)
@pytest.mark.parametrize(
    ['nearest_zone', 'country_enabled'],
    [('Москва', True), ('Балашиха', False)],
)
async def test_post_accident_create_ticket(
        pgsql,
        confidence,
        confidence_need_create_ticket,
        confidence_need_send_push,
        nearest_zone,
        country_enabled,
        web_app_client,
        mock_chatterbox_py3,
        mock_archive_response,
        is_tariff_disabled,
):
    scenario = PostTestScenario(
        scenario_type='insert',
        awaited_status=200,
        accident=data_generators.generated_accident(1),
        patches=[{'confidence': confidence}],
        user_id='user_id1',
    )
    need_create_ticket = all(
        [
            confidence_need_create_ticket,
            country_enabled,
            not is_tariff_disabled,
        ],
    )
    need_send_push = all(
        [not need_create_ticket, confidence_need_send_push, country_enabled],
    )

    @mock_chatterbox_py3('/v1/tasks/init/customer_care')
    def _v1_tasks_init_customer_care_post(request):
        assert need_create_ticket
        assert request.json['order_id'] == 'order_id1'
        return {}

    archive_response = copy.deepcopy(DEFAULT_ARCHIVE_RESPONSE)
    archive_response['nz'] = nearest_zone
    mock_archive_response(archive_response)

    with asynctest.patch.object(push_logic, 'send_push') as send_push_patch:
        response = await web_app_client.post(
            ACCIDENTS_HANDLE_PATH,
            data=json.dumps(scenario.accident.serialize()),
        )

        await scenario.verify_response(response, pgsql)
        assert _v1_tasks_init_customer_care_post.times_called == int(
            need_create_ticket,
        )
        if need_send_push:
            send_push_patch.assert_awaited_once()
        else:
            send_push_patch.assert_not_awaited()


@pytest.mark.pgsql(
    'safety_center',
    queries=[
        data_generators.insert_accident_query(0, confidence=0),
        data_generators.insert_accident_query(
            1, confidence=DEFAULT_CONFIDENCE,
        ),
    ],
)
@pytest.mark.config(
    SAFETY_CENTER_PUSH_SETTINGS=DEFAULT_ACCIDENTS_CONFIG,
    SAFETY_CENTER_CREATE_CHATTERBOX_TICKET_ENABLED=True,
    SAFETY_CENTER_CHATTERBOX_TICKET_SETTINGS=dict(
        threshold=DEFAULT_CONFIDENCE, macros_ids=[0], countries=['rus'],
    ),
)
@pytest.mark.parametrize(
    ['accident_id', 'need_create_ticket'], [(0, True), (1, False)],
)
async def test_post_accident_update_create_ticket(
        pgsql,
        accident_id,
        need_create_ticket,
        web_app_client,
        mock_chatterbox_py3,
        mock_archive_response,
):
    scenario = PostTestScenario(
        scenario_type='update',
        awaited_status=200,
        accident=data_generators.generated_accident(
            accident_id, generate_id=True,
        ),
        patches=[data_generators.generated_accident_dict(2)],
    )

    @mock_chatterbox_py3('/v1/tasks/init/customer_care')
    def _v1_tasks_init_customer_care_post(request):
        assert need_create_ticket
        assert request.json['order_id'] == 'order_id' + str(accident_id)
        return {}

    archive_response = copy.deepcopy(DEFAULT_ARCHIVE_RESPONSE)
    archive_response['nz'] = 'Москва'
    mock_archive_response(archive_response)

    response = await web_app_client.post(
        ACCIDENTS_HANDLE_PATH, data=json.dumps(scenario.accident.serialize()),
    )

    await scenario.verify_response(response, pgsql)
    assert _v1_tasks_init_customer_care_post.times_called == int(
        need_create_ticket,
    )
