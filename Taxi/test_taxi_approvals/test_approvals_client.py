# pylint: disable=unused-variable
import typing

import pytest

from taxi.util.aiohttp_kit import api

from taxi_approvals.internal import types as ts


@pytest.mark.parametrize(
    'data',
    [
        {
            'service_name': 'test_service',
            'api_path': 'test_api',
            'request_id': 'test_id',
            'run_manually': True,
            'data': {'test_data_key': 'test_data_value'},
            'description': 'just_random_comment',
            'mode': 'push',
        },
    ],
)
async def test_client_create_draft(taxi_approvals_client, data, mockserver):
    taxi_approvals_app = taxi_approvals_client.app
    context = typing.cast(ts.WebContext, taxi_approvals_app.ctx)

    @mockserver.json_handler('/taxi_approvals/drafts/create/')
    def draft_create(request):
        validator = context.services_schemes.json_validators[
            'drafts.yaml#/definitions/CreateDraftRequest'
        ]
        error_response = api.validate_data(validator, request.json, True)
        assert error_response is None
        return {}

    await taxi_approvals_app.approvals_client.create_draft(data, 'mvpetrov')


async def test_client_manual_apply(taxi_approvals_client, mockserver):
    taxi_approvals_app = taxi_approvals_client.app
    context = typing.cast(ts.WebContext, taxi_approvals_app.ctx)

    @mockserver.json_handler(r'/taxi_approvals/drafts/', prefix=True)
    def draft_create(request):
        validator = context.services_schemes.json_validators[
            'drafts.yaml#/definitions/ServiceNameParameter'
        ]
        error_response = api.validate_data(validator, request.json, True)
        assert error_response is None
        return {}

    await taxi_approvals_app.approvals_client.manual_apply('123', 'mvpetrov')
