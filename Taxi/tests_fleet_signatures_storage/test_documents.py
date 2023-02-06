import pytest

DOCUMENT_1 = {
    'id': '00000001-f462-48af-bb10-66b0e9942bd8',
    'body': 'dGVzdF9kb2N1bWVudF8y',
    'signatures': [
        {
            'id': '00000002-4878-49b7-b203-62135cb951df',
            'signed_by': {
                'identity': 'dispatcher',
                'park_id': 'park_1',
                'dispatcher_id': 'dispatcher_1',
            },
            'type': 'simple',
            'signed_at': '2020-04-10T08:25:18+00:00',
        },
        {
            'id': '00000002-80b0-41cf-8eaf-52ed0a54e88c',
            'signed_by': {'identity': 'unknown'},
            'type': 'qualified',
            'data': 'dGVzdF9zaWduYXR1cmU=',
            'signed_at': '2020-04-10T08:25:18+00:00',
        },
    ],
}

NEW_DOCUMENT_1 = {
    'id': '00000001-059a-4806-ac1f-2abd117322f0',
    'body': 'dGVzdF9kb2N1bWVudA==',
    'signatures': [
        {
            'id': '00000002-860c-4f37-9293-724fca18e75e',
            'signed_by': {
                'identity': 'driver',
                'park_id': 'park_1',
                'driver_profile_id': 'driver_1',
            },
            'type': 'simple',
            'signed_at': '2020-04-09T08:25:18+00:00',
        },
    ],
}

NEW_SIGNATURE_1 = {
    'id': '00000002-736b-4899-8f83-3da154f6ce74',
    'signed_by': {
        'identity': 'driver',
        'park_id': 'park_1',
        'driver_profile_id': 'driver_1',
    },
    'type': 'simple',
    'signed_at': '2020-04-10T08:25:18+00:00',
}


@pytest.mark.pgsql('fleet_signatures_storage', files=['signatures.sql'])
@pytest.mark.parametrize(
    'request_body, expected_status_code', [(NEW_DOCUMENT_1, 200)],
)
async def test_documents_post(
        taxi_fleet_signatures_storage, request_body, expected_status_code,
):
    response = await taxi_fleet_signatures_storage.post(
        '/v1/documents', json=request_body,
    )

    assert response.status_code == expected_status_code


@pytest.mark.pgsql('fleet_signatures_storage', files=['signatures.sql'])
@pytest.mark.parametrize(
    'document_id, expected_status_code, expected_body',
    [(DOCUMENT_1['id'], 200, DOCUMENT_1), (NEW_DOCUMENT_1['id'], 404, None)],
)
async def test_documents_item_get(
        taxi_fleet_signatures_storage,
        document_id,
        expected_status_code,
        expected_body,
):
    response = await taxi_fleet_signatures_storage.get(
        '/v1/documents/item', params={'document_id': document_id},
    )

    assert response.status_code == expected_status_code
    if expected_body:
        assert response.json() == expected_body


@pytest.mark.pgsql('fleet_signatures_storage', files=['signatures.sql'])
@pytest.mark.parametrize(
    'document_id, request_body, expected_status_code',
    [
        (DOCUMENT_1['id'], NEW_SIGNATURE_1, 200),
        (NEW_DOCUMENT_1['id'], NEW_SIGNATURE_1, 400),
    ],
)
async def test_documents_item_add_signature_post(
        taxi_fleet_signatures_storage,
        document_id,
        request_body,
        expected_status_code,
):
    response = await taxi_fleet_signatures_storage.post(
        '/v1/documents/item/signatures',
        params={'document_id': document_id},
        json=request_body,
    )

    assert response.status_code == expected_status_code
