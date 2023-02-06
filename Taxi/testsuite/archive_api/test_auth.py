import pytest


HANDLERS_READ = [
    'archive/order',
    'archive/orders',
    'v1/yt/lookup_rows',
    'v1/yt/select_rows',
]

HANDLERS_WRITE = [
    'archive/orders/restore',
    'archive/order_proc/restore',
    'archive/mph_results/restore',
    'archive/subvention_reasons/restore',
]

TVM_TICKET = (
    '3:serv:CBAQ__________9_IgQIexAf:LrJTnOV5PryB95dOPIv-4osNDxJ3m84dgNADONFtU'
    'DG-u8-B4Od8a8Kr3pWnehiP1178B4T1WWJ4X2naNEzwdGcXhS1LClSDH87zUKgOl38iX5ZUHB'
    'VL7ftE1hmxNBh8qeagn6kNrVNywJ76Y_RC71iXW2hATCL5FH9Cz6cyn60'
)


@pytest.mark.parametrize('handler_name', HANDLERS_READ + HANDLERS_WRITE)
def test_wrong_token(taxi_archive_api, yt_client, handler_name):
    response = taxi_archive_api.post(
        handler_name,
        headers={'YaTaxi-Api-Key': 'wrong_token'},
        json={'param': 'archive_api_order_id'},
    )
    assert response.status_code == 401


@pytest.mark.parametrize('handler_name', HANDLERS_READ + HANDLERS_WRITE)
def test_wrong_token_ok_tvm(taxi_archive_api, yt_client, handler_name):
    response = taxi_archive_api.post(
        handler_name,
        headers={
            'YaTaxi-Api-Key': 'wrong_token',
            'X-Ya-Service-Ticket': TVM_TICKET,
        },
        json={'param': 'archive_api_order_id'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('handler_name', HANDLERS_READ + HANDLERS_WRITE)
def test_read_token(taxi_archive_api, yt_client, handler_name):
    response = taxi_archive_api.post(
        handler_name,
        headers={'YaTaxi-Api-Key': 'archive_api_token_read'},
        json={'param': 'archive_api_order_id'},
    )
    expected_code = 400 if handler_name in HANDLERS_READ else 401
    assert response.status_code == expected_code
