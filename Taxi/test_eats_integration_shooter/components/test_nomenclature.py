import json

import pytest


@pytest.mark.parametrize(
    'stocks_file, errors_list, is_catch_weight',
    [
        ['data_nomenclature.json', [], False],
        [
            'data_nomenclature_errors.json',
            [
                'Отсутствует обязательное поле images.0.hash для категории, айди категории - monday_msk',  # noqa: F401,E501
                'Некорректный id категории, порядковый номер - 1',  # noqa: F401,E501
                'Некорректное значение категории для name, айди категории - 1234',  # noqa: F401,E501
                'Некорректное значение категории images:\'22\', отличающееся от array, айди категории - ribnaya_tarelka2',  # noqa: F401,E501
                'Отсутствует обязательное поле barcode.value для товара, айди товара - 237439',  # noqa: F401,E501
                'Некорректное значение товара isCatchWeight:None, отличающееся от boolean, айди товара - 237439',  # noqa: F401,E501
                'Некорректное значение товара measure.unit:M, отличающееся от значений списка ENUM [\'MLT\', \'GRM\'], айди товара - 237439',  # noqa: F401,E501
                'Некорректное значение товара vat:\'20\', отличающееся от integer, айди товара - 237439',  # noqa: F401,E501
                'Отсутствует обязательное поле categoryId для товара, айди товара - 237439',  # noqa: F401,E501
                'Отсутствует обязательное поле barcode.value для товара, айди товара - 237440',  # noqa: F401,E501
                'Некорректное значение товара для description.vendorName, айди товара - 237440',  # noqa: F401,E501
                'Некорректное значение товара isCatchWeight:0, отличающееся от boolean, айди товара - 237440',  # noqa: F401,E501
                'Некорректное значение товара measure.unit:M, отличающееся от значений списка ENUM [\'MLT\', \'GRM\'], айди товара - 237440',  # noqa: F401,E501
                'Некорректное значение товара vat:\'20\', отличающееся от integer, айди товара - 237440',  # noqa: F401,E501
                'Некорректное весовое значение для measure.quantum, айди товара - 457335',  # noqa: F401,E501
                'Не уникальный id категории(id:ribnaya_tarelka), порядковый номер - 6',  # noqa: F401,E501
                'Товар items.id:457335 - ссылается на несуществующую категорию в items.categoryId:00048000',  # noqa: F401,E501
            ],
            True,
        ],
    ],
)
async def test_nomenclature(
        web_context,
        mockserver,
        load_json,
        stocks_file,
        errors_list,
        is_catch_weight,
):
    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')),
            200,
            headers={'Content-type': 'application/json'},
        )

    @mockserver.handler(f'/nomenclature/123/composition')
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
        'is_catch_weight': is_catch_weight,
    }
    response = await web_context.nomenclature_worker.validate_nomenclature(
        request_param,
    )
    assert errors_list == response
    assert get_test_get_token.has_calls
    assert mock_get_items.has_calls
