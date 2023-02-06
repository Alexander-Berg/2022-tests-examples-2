from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_tags.tags import constants
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools


_MANUAL = tags_tools.Provider(
    provider_id=1000, name='man', desc='man_desc', is_active=True,
)
_SERVICE_BASE = tags_tools.Provider(
    provider_id=1001,
    name='service-base',
    desc='service_base',
    is_active=False,
)
_SERVICE_AUDITED = tags_tools.Provider(
    provider_id=1002,
    name='service-audited',
    desc='service_audited',
    is_active=True,
)
_MAP_REDUCE = tags_tools.Provider(
    provider_id=1003, name='map-reduce', desc='chyt', is_active=False,
)


def _get_body_from(
        provider: tags_tools.Provider,
        kind: str,
        authority: str = 'base',
        tvm_owners: List[str] = None,
):
    return {
        'type': kind,
        'is_active': provider.is_active,
        'acl': {'authority': authority, 'tvm_owners': tvm_owners or list()},
    }


def _insert_service_provider(
        provider_id: int, tvm_owners: List[str], authority: str,
):
    owners = '{' + ','.join('\"' + name + '\"' for name in tvm_owners) + '}'
    return (
        f'INSERT INTO service.providers '
        f'(provider_id, service_names, authority) '
        f'VALUES ({provider_id}, \'{owners}\', \'{authority}\')'
    )


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [_MANUAL, _SERVICE_BASE, _SERVICE_AUDITED, _MAP_REDUCE],
        ),
        _insert_service_provider(_SERVICE_BASE.provider_id, ['abc'], 'base'),
        _insert_service_provider(
            _SERVICE_AUDITED.provider_id, ['abc', 'idm'], 'audited',
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    name=_MAP_REDUCE.name,
                    provider_id=_MAP_REDUCE.provider_id,
                    tags=['chyt'],
                    enabled=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'provider, expected_code, expected_body',
    [
        pytest.param(
            _MANUAL.name,
            200,
            _get_body_from(_MANUAL, kind='manual'),
            id='manual',
        ),
        pytest.param(
            _SERVICE_BASE.name,
            200,
            _get_body_from(_SERVICE_BASE, kind='service', tvm_owners=['abc']),
            id='service_base',
        ),
        pytest.param(
            _SERVICE_AUDITED.name,
            200,
            _get_body_from(
                _SERVICE_AUDITED,
                kind='service',
                authority='audited',
                tvm_owners=['abc', 'idm'],
            ),
            id='service_audited',
        ),
        pytest.param(
            _MAP_REDUCE.name,
            200,
            _get_body_from(_MAP_REDUCE, kind='yql'),
            id='yql',
        ),
        pytest.param(
            'unknown',
            404,
            {'code': '404', 'message': 'provider not found'},
            id='not_found',
        ),
    ],
)
async def test_get(
        taxi_tags,
        provider: str,
        expected_code: int,
        expected_body: Dict[str, Any],
):
    response = await taxi_tags.get(f'/v1/segments/providers/{provider}')
    assert response.status_code == expected_code
    assert response.json() == expected_body


def _create_request(
        is_active: bool = True,
        description: str = 'provider description',
        authority: str = 'base',
        tvm_owners: List[str] = None,
):
    return {
        'is_active': is_active,
        'description': description,
        'acl': {'authority': authority, 'tvm_owners': tvm_owners or list()},
    }


_TVM_SOURCE = 'reposition'
_FORBIDDEN_BY_TVM = {
    'code': 'FORBIDDEN',
    'message': 'only service from acl.tvm_owners can create service provider',
}
_FORBIDDEN_BY_AUTHORITY = {
    'code': 'FORBIDDEN',
    'message': 'only base non audited providers are allowed to be created',
}
_CONFLICT = {
    'code': 'CONFLICT',
    'message': 'provider already exists and has different attributes',
}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [_MANUAL, _SERVICE_BASE, _SERVICE_AUDITED, _MAP_REDUCE],
        ),
        _insert_service_provider(
            _SERVICE_BASE.provider_id, [_TVM_SOURCE], 'base',
        ),
        _insert_service_provider(
            _SERVICE_AUDITED.provider_id, ['abc', 'idm'], 'audited',
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    name=_MAP_REDUCE.name,
                    provider_id=_MAP_REDUCE.provider_id,
                    tags=['chyt'],
                    enabled=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'provider, sign_with_tvm, body, expected_code, expected_body',
    [
        pytest.param(
            'new-name',
            _TVM_SOURCE,
            _create_request(tvm_owners=list()),
            403,
            _FORBIDDEN_BY_TVM,
            id='no_tvm_owners',
        ),
        pytest.param(
            'new-name',
            _TVM_SOURCE,
            _create_request(tvm_owners=[_TVM_SOURCE, 'some-other-service']),
            200,
            dict(),
            id='success',
        ),
        pytest.param(
            'new-name',
            _TVM_SOURCE,
            _create_request(tvm_owners=[_TVM_SOURCE], authority='audited'),
            403,
            _FORBIDDEN_BY_AUTHORITY,
            id='forbidden_by_audited_authority',
        ),
        pytest.param(
            'new-name',
            None,
            _create_request(tvm_owners=[_TVM_SOURCE, 'some-other-service']),
            403,
            _FORBIDDEN_BY_TVM,
            id='no_tvm_sign',
        ),
        pytest.param(
            'new-name',
            _TVM_SOURCE,
            _create_request(tvm_owners=['some-other-service']),
            403,
            _FORBIDDEN_BY_TVM,
            id='attempt_to_create_other_tvm_provider',
        ),
        pytest.param(
            _SERVICE_BASE.name,
            _TVM_SOURCE,
            _create_request(
                _SERVICE_BASE.is_active,
                _SERVICE_BASE.desc,
                'base',
                [_TVM_SOURCE],
            ),
            200,
            dict(),
            id='trait_existing_as_creation_retry',
        ),
        pytest.param(
            _SERVICE_BASE.name,
            _TVM_SOURCE,
            _create_request(
                (not _SERVICE_BASE.is_active),
                _SERVICE_BASE.desc,
                'base',
                [_TVM_SOURCE],
            ),
            409,
            _CONFLICT,
            id='existing_provider_differs_by_activity',
        ),
        pytest.param(
            _SERVICE_BASE.name,
            _TVM_SOURCE,
            _create_request(
                _SERVICE_BASE.is_active,
                _SERVICE_BASE.desc,
                'base',
                ['some-other', _TVM_SOURCE],
            ),
            409,
            _CONFLICT,
            id='existing_provider_differs_by_owners',
        ),
        pytest.param(
            _MAP_REDUCE.name,
            _TVM_SOURCE,
            _create_request(tvm_owners=[_TVM_SOURCE]),
            409,
            _CONFLICT,
            id='already_exists_a_yql',
        ),
        pytest.param(
            _MANUAL.name,
            _TVM_SOURCE,
            _create_request(tvm_owners=[_TVM_SOURCE]),
            409,
            _CONFLICT,
            id='already_exists_manual',
        ),
        pytest.param(
            _SERVICE_AUDITED.name,
            _TVM_SOURCE,
            _create_request(tvm_owners=[_TVM_SOURCE]),
            409,
            _CONFLICT,
            id='already_exists_service',
        ),
        pytest.param(
            'unreasonable::provider*name',
            _TVM_SOURCE,
            _create_request(tvm_owners=[_TVM_SOURCE]),
            400,
            None,
            id='invalid_provider_name',
        ),
    ],
)
async def test_create(
        taxi_tags,
        taxi_config,
        load,
        provider: str,
        sign_with_tvm: Optional[str],
        body: Dict[str, Any],
        expected_code: int,
        expected_body: Optional[Dict[str, Any]],
):
    taxi_config.set_values(dict(TVM_ENABLED=(sign_with_tvm is not None)))

    headers: Dict[str, Any] = {}
    if sign_with_tvm:
        constants.add_tvm_header(load, headers, sign_with_tvm)

    response = await taxi_tags.post(
        f'/v1/segments/providers/{provider}/create',
        json=body,
        headers=headers,
    )
    assert response.status_code == expected_code
    if expected_body:
        assert response.json() == expected_body
