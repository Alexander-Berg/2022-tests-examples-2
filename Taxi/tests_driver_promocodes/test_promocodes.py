import pytest

from . import utils

HEADERS = {'X-Yandex-Login': 'vdovkin'}
# Generated via `tvmknife unittest service -s 2020527 -d 2020527`
PROMOCODES_TICKET = (
    '3:serv:CBAQ__________9_IggIr6l7EK-pew:JDDmKdfGuACYhSKVXG'
    'UFESNoA6lQMeMul8NDJEXxBotkpTNSlWLu8EpC_95SgsHqCxhelXTaJs'
    'ZLD_IsUXf-g3Yr-t79TF1CGXl9-5IwkhVFHT1sXxae-uh_OiWvNK7PoG'
    'GlcZWZDeRPkvCR9zfZ1vx3fAE94Tv1QOlL-u7CAFY'
)
# Generated via `tvmknife unittest service -s 111 -d 2020527`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxCvqXs:CVDEtdtqrs0R8h1GQPKNFfkRf0O'
    '2e-0G4tKqOIEcMxRA3WSiAzU51HWeC39gVpxXhNCDrgNjVfdsT5EudT-IJpKXP'
    'fB4IYRXXFClXOdtFcRuB1wP5hXDG-0M8A6THzrN1xgMPmD4wyLNExcCrIY5srk'
    'r9m5EPsC6D5LR-UFZspg'
)


@pytest.mark.pgsql('driver_promocodes', files=['series.sql', 'promocodes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'request_create,response_create,response_list_after,is_good',
    [
        (
            'request_create_ok.json',
            'response_create.json',
            'response_list_after.json',
            True,
        ),
        ('request_create_over_limit.json', None, None, False),
        ('request_create_bad_driver.json', None, None, False),
    ],
)
async def test_driver_promocodes_add_admin(
        taxi_driver_promocodes,
        parks,
        load_json,
        request_create,
        response_create,
        response_list_after,
        is_good,
):
    response = await taxi_driver_promocodes.post(
        'admin/v1/promocodes', json=load_json(request_create), headers=HEADERS,
    )
    assert response.status_code == (200 if is_good else 400)

    if response_create:
        assert utils.remove_not_testable(
            response.json(),
        ) == utils.remove_not_testable(load_json(response_create))

    if response_list_after:
        response = await taxi_driver_promocodes.get(
            'admin/v1/promocodes/list', params={},
        )
        assert (
            utils.remove_not_testable_promocodes(response.json())
            == utils.remove_not_testable_promocodes(
                load_json(response_list_after),
            )
        )


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'internal-service', 'dst': 'driver-promocodes'}],
    TVM_SERVICES={'driver-promocodes': 2020527, 'internal-service': 111},
)
@pytest.mark.tvm2_ticket({2020527: PROMOCODES_TICKET, 111: MOCK_TICKET})
@pytest.mark.pgsql('driver_promocodes', files=['series.sql', 'promocodes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'request_create,response_create,response_list_after,attempts,user,is_good',
    [
        (
            'request_create_ok.json',
            'response_create_service.json',
            'response_list_after_service.json',
            2,
            None,
            True,
        ),
        (
            'request_create_ok.json',
            'response_create_service_user.json',
            None,
            2,
            'vdovkin',
            True,
        ),
        ('request_create_over_limit.json', None, None, 1, None, False),
        ('request_create_bad_driver.json', None, None, 1, None, False),
    ],
)
async def test_driver_promocodes_add_internal(
        taxi_driver_promocodes,
        parks,
        load_json,
        request_create,
        response_create,
        response_list_after,
        attempts,
        user,
        is_good,
):
    for _ in range(attempts):
        headers = {
            'X-Ya-Service-Ticket': MOCK_TICKET,
            'X-Idempotency-Token': 'token123',
        }
        if user:
            headers['X-Yandex-Login'] = user
        response = await taxi_driver_promocodes.post(
            'internal/v1/promocodes',
            json=load_json(request_create),
            headers=headers,
        )
        assert response.status_code == (200 if is_good else 400)
        if response_create:
            assert utils.remove_not_testable(
                response.json(),
            ) == utils.remove_not_testable(load_json(response_create))

    if response_list_after:
        response = await taxi_driver_promocodes.get(
            'admin/v1/promocodes/list',
            params={},
            headers={'X-Ya-Service-Ticket': MOCK_TICKET},
        )
        assert (
            utils.remove_not_testable_promocodes(response.json())
            == utils.remove_not_testable_promocodes(
                load_json(response_list_after),
            )
        )
