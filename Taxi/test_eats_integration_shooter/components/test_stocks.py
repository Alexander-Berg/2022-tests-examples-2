import json

import pytest


@pytest.mark.parametrize(
    'stocks_file, errors_list',
    [
        ['data_stocks.json', []],
        [
            'data_stocks_errors.json',
            [
                'Некорректный id для товара({\'stock\': 0}) '
                'порядковый номер - 0',
                'Некорректное значение {\'stock\': \'12\'}. '
                'Айди товара - 46956',
                'Некорректное значение {\'stock\': -1}. Айди товара - 51201',
            ],
        ],
    ],
)
async def test_stocks(
        web_context, mockserver, load_json, stocks_file, errors_list,
):
    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')),
            200,
            headers={'Content-type': 'application/json'},
        )

    @mockserver.handler(f'/nomenclature/123/availability')
    def mock_get_items(request):
        return mockserver.make_response(
            json.dumps(load_json(stocks_file)),
            200,
            headers={
                'Content-type': (
                    'application/vnd.eda.picker.nomenclature.v1+json'
                ),
            },
        )

    request_param = {
        'vendor_host': '$mockserver',
        'client_id': 'yandex',
        'client_secret': 'client_secret',
        'grant_type': 'grant_type',
        'scope': 'scope',
        'origin_id': '123',
    }
    response = await web_context.stocks_worker.validate_stocks(request_param)
    assert errors_list == response
    assert get_test_get_token.has_calls
    assert mock_get_items.has_calls
