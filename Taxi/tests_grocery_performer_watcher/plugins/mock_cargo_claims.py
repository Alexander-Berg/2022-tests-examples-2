# pylint: disable=import-only-modules, unsubscriptable-object, invalid-name
# flake8: noqa IS001
from dataclasses import dataclass
from typing import Optional

import pytest

from tests_grocery_performer_watcher.plugins.service_mock import (
    EndpointContext,
    ServiceContext,
    make_response,
)


@dataclass
class V2ClaimsFullContext(EndpointContext):
    file_name: str = 'cargo-claims/claim_full_response.json'


@pytest.fixture(name='v2_claims_full')
def _v2_claims_full(mockserver, load_json):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    async def handler(request):
        assert request.query['claim_id'] == context.claim_id

        if context.error:
            return context.make_error_response()
        if context.response:
            return context.response

        segment = load_json(context.file_name)
        return make_response(json=segment, status=200)

    context = V2ClaimsFullContext(mock=handler)
    return context


@dataclass
class CargoClaimsContext(ServiceContext):
    v2_claims_full: V2ClaimsFullContext

    claim_id: str = 'CLAIM_ID_1'


@pytest.fixture(name='cargo_claims')
def _cargo_claims(v2_claims_full):
    return CargoClaimsContext(v2_claims_full=v2_claims_full)
