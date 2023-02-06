import pytest

from tests_card_antifraud import configs


@pytest.mark.parametrize(
    ('request_body', 'headers', 'expected_code', 'expected_status'),
    [
        ({'verification_id': 'a1234'}, {'X-Yandex-Uid': '1234'}, 404, None),
        (
            {'verification_id': 'a1235'},
            {'X-Yandex-Uid': '1235'},
            200,
            'in_progress',
        ),
        (
            {'verification_id': 'a1236'},
            {'X-Yandex-Uid': '1236'},
            200,
            'success',
        ),
        (
            {'verification_id': 'a1237'},
            {'X-Yandex-Uid': '1237'},
            200,
            'failure',
        ),
        ({'verification_id': 'a1238'}, {'X-Yandex-Uid': '1238'}, 500, None),
        ({'verification_id': 'a1240'}, {'X-Yandex-Uid': '1240'}, 500, None),
        (
            {'verification_id': 'a1239'},
            {'X-Yandex-Uid': '1239'},
            200,
            'cvn_expected',
        ),
        (
            {'verification_id': 'purchase_1241'},
            {'X-Yandex-Uid': '1241'},
            200,
            '3ds_required',
        ),
    ],
)
async def test_verifications_status(
        taxi_card_antifraud,
        request_body,
        headers,
        expected_code,
        expected_status,
):
    response = await taxi_card_antifraud.get(
        '/4.0/payment/verifications/status',
        params=request_body,
        headers=headers,
    )
    assert expected_code == response.status_code

    if expected_code == 200:
        assert expected_status == response.json()['status']


@pytest.mark.config(CARD_ANTIFRAUD_SERVICE_ENABLED=False)
@pytest.mark.parametrize(
    ('request_body', 'headers', 'expected_code'),
    [({'verification_id': 'a1234'}, {'X-Yandex-Uid': '1234'}, 429)],
)
async def test_verifications_status_service_disabled(
        taxi_card_antifraud, request_body, headers, expected_code,
):
    response = await taxi_card_antifraud.get(
        '/4.0/payment/verifications/status',
        params=request_body,
        headers=headers,
    )
    assert expected_code == response.status_code


async def test_change_3ds_host(taxi_card_antifraud, experiments3):
    header_host = 'header-host'
    changed_url = f'https://{configs.CHANGED_HOST}/process_3ds?id=123'

    configs.use_binding_form_host(experiments3, expected_header=header_host)

    response = await taxi_card_antifraud.get(
        '/4.0/payment/verifications/status',
        headers={'X-Yandex-Uid': '1242', 'X-YProxy-Header-Host': header_host},
        params={'verification_id': 'a1242'},
    )

    assert response.status_code == 200
    assert response.json()['3ds_url'] == changed_url
