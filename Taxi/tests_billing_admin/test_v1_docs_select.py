import dataclasses
import json

import pytest

from tests_billing_admin import blueprints

DRIVER_TAG = 'taxi/entity_id/taximeter_driver_id/some_db_id/some_uuid'
PAST = '1970-01-01T00:00:00+00:00'
FUTURE = '2119-02-12T00:00:00+00:00'


@dataclasses.dataclass(frozen=True)
class ApiSpec:
    path: str
    expected_request: dict
    response: dict
    status_code: int = 200
    call_make_response: bool = False


def archive_order_proc_spec(id_, order_proc):
    response = blueprints.responses.archive_api(order_proc)
    return ApiSpec(
        '/order-archive/v1/order_proc/retrieve',
        expected_archive_request(id_),
        response,
        call_make_response=True,
    )


def not_found_archive_order_proc_spec(id_):
    # pylint: disable=invalid-name
    return ApiSpec(
        '/order-archive/v1/order_proc/retrieve',
        expected_archive_request(id_),
        response=json.dumps({'text': ''}),
        status_code=404,
        call_make_response=True,
    )


def expected_archive_request(id_):
    return {'id': id_, 'indexes': ['reorder', 'alias'], 'lookup_yt': True}


def docs_select_spec(external_obj_id):
    expected_request = {
        'external_obj_id': external_obj_id,
        'begin_time': PAST,
        'end_time': FUTURE,
        'cursor': {},
        'limit': 100,
    }
    docs = [blueprints.docs.input_rebill_order()]
    response = blueprints.responses.billing_reports_docs(docs)
    return ApiSpec(
        'billing-reports/v1/docs/select', expected_request, response,
    )


def docs_by_tag_spec(
        tag, docs=None, begin_time=None, end_time=None, cursor=None,
):
    if docs is None:
        docs = [blueprints.docs.input_rebill_order()]
    if begin_time is None:
        begin_time = PAST
    if end_time is None:
        end_time = FUTURE

    expected_request = {
        'tag': tag,
        'begin_time': begin_time,
        'end_time': end_time,
        'limit': 100,
    }
    if cursor is not None:
        expected_request['cursor'] = cursor
    response = blueprints.responses.billing_reports_docs(
        docs, cursor_type='str',
    )
    return ApiSpec(
        'billing-reports/v1/docs/by_tag', expected_request, response,
    )


def mock_api(mockserver, spec):
    @mockserver.json_handler(spec.path)
    def _handler(request):
        assert request.json == spec.expected_request
        if spec.call_make_response:
            return mockserver.make_response(
                spec.response, status=spec.status_code,
            )
        return spec.response


def make_driver_query(db_id, uuid):
    return {
        'driver': {'db_id': db_id, 'uuid': uuid},
        'begin_time': '2018-01-01T00:00:00+00:00',
        'end_time': '2019-01-01T00:00:00+00:00',
    }


def make_unique_driver_id_query():
    return {
        'unique_driver_id': '5bab4bf979b9e5513fe5ec4a',
        'date': '2020-02-26',
        'rule_type': 'nmfg',
    }


def make_response(docs, cursor=None):
    if cursor is None:
        cursor = blueprints.responses.cursor()
    return {'docs': docs, 'cursor': cursor}


@pytest.mark.parametrize(
    'query, cursor, api_specs, expected_response',
    [
        (
            {'topic': 'alias_id/some_alias_id'},
            {},
            [docs_select_spec('alias_id/some_alias_id')],
            make_response([blueprints.docs.output_rebill_order()]),
        ),
        (
            {'parent_doc_id': 4294967296},
            {},
            [docs_by_tag_spec('system://parent_doc_id/4294967296')],
            make_response(
                [blueprints.docs.output_rebill_order()],
                blueprints.responses.wrapped_str_cursor(),
            ),
        ),
        (
            {'parent_doc_id': 4294967296},
            {'reports_cursor': 'billing_reports_cursor'},
            [
                docs_by_tag_spec(
                    'system://parent_doc_id/4294967296',
                    cursor='billing_reports_cursor',
                ),
            ],
            make_response(
                [blueprints.docs.output_rebill_order()],
                blueprints.responses.wrapped_str_cursor(),
            ),
        ),
        (
            make_driver_query('some_db_id', 'some_uuid'),
            {},
            [
                docs_by_tag_spec(
                    DRIVER_TAG,
                    begin_time='2018-01-01T00:00:00+00:00',
                    end_time='2019-01-01T00:00:00+00:00',
                ),
            ],
            make_response(
                [blueprints.docs.output_rebill_order()],
                blueprints.responses.wrapped_str_cursor(),
            ),
        ),
        (
            {'any_order_id': 'unknown_order_id'},
            {},
            [not_found_archive_order_proc_spec('unknown_order_id')],
            make_response([], {}),
        ),
        (
            {'any_order_id': 'some_order_id'},
            {},
            [
                archive_order_proc_spec(
                    'some_order_id',
                    blueprints.responses.assigned_order_proc(),
                ),
                docs_by_tag_spec('taxi/alias_id/some_alias_id'),
            ],
            make_response(
                [blueprints.docs.output_rebill_order()],
                blueprints.responses.wrapped_str_cursor(),
            ),
        ),
        (
            {'any_order_id': 'unassigned_order_id'},
            {},
            [
                archive_order_proc_spec(
                    'unassigned_order_id',
                    blueprints.responses.unassigned_order_proc(),
                ),
            ],
            make_response([], {}),
        ),
        (
            make_unique_driver_id_query(),
            {},
            [
                docs_by_tag_spec(
                    'taxi/shift_ended/unique_driver_id/'
                    '5bab4bf979b9e5513fe5ec4a/2020-02-26/nmfg',
                    begin_time='1970-01-01T00:00:00+00:00',
                    end_time='2119-02-12T00:00:00+00:00',
                ),
            ],
            make_response(
                [blueprints.docs.output_rebill_order()],
                blueprints.responses.wrapped_str_cursor(),
            ),
        ),
    ],
)
@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_v1_docs_select(
        query,
        cursor,
        api_specs,
        expected_response,
        mockserver,
        taxi_billing_admin,
):

    for spec in api_specs:
        mock_api(mockserver, spec)

    response = await taxi_billing_admin.post(
        'v1/docs/select',
        json={'query': query, 'cursor': cursor, 'limit': 100},
    )
    assert_is_successfull(response)
    assert response.json() == expected_response


def assert_is_successfull(response):
    assert response.status_code == 200, response.content
