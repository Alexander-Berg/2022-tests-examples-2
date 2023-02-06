import datetime as dt
import json

from tests_eats_order_revision import helpers

MIXIN_UPDATE_HANDLER = (
    '/v1/order-revision/customer-services/mixins/update?order_id=test_order&'
)

CUSTOMER_SERVICE_MIXINS_REQUEST = {
    'customer_service_mixins': [
        {
            'customer_service_id': 'customer_service_id_1',
            'mixins': [
                {'discriminator_type': 'vat', 'value': 'nds_18'},
                {
                    'discriminator_type': 'personal_tin_id',
                    'value': 'personal_tin_id_1',
                },
                {
                    'discriminator_type': 'balance_client_id',
                    'value': 'balance_client_id_1',
                },
            ],
        },
    ],
}


async def test_update_mixins(taxi_eats_order_revision, pgsql, load_json):
    """
    Тест проверяет обновление таблицы миксинов.
    """
    doc = load_json('revisions_without_details/revision_doc.json')
    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision',
        document=json.dumps(doc),
        created_at=dt.datetime.now(),
    )
    helpers.insert_default_mixins(pgsql, load_json)

    response = await taxi_eats_order_revision.put(
        MIXIN_UPDATE_HANDLER, json=CUSTOMER_SERVICE_MIXINS_REQUEST,
    )

    mixin = helpers.fetch_revision_mixin_payload(
        pgsql, 'test_order', 'customer_service_id_1',
    )

    assert response.status == 200

    assert mixin['vat'] == 'nds_18'
    assert mixin['personal_tin_id'] == 'personal_tin_id_1'
    assert mixin['balance_client_id'] == 'balance_client_id_1'


async def test_update_mixins_400(taxi_eats_order_revision, pgsql, load_json):
    """
    Тест проверяет, что если запрос невалидный, то ручка вернет 400.
    """
    doc = load_json('revisions_without_details/revision_doc.json')
    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision',
        document=json.dumps(doc),
        created_at=dt.datetime.now(),
    )
    helpers.insert_default_mixins(pgsql, load_json)

    response = await taxi_eats_order_revision.put(
        '/v1/order-revision/customer-services/mixins/update?order_id=fake_id&',
        json={},
    )

    assert response.status == 400


async def test_update_mixins_404(taxi_eats_order_revision, pgsql, load_json):
    """
    Тест проверяет, что если ревизии с таким
    order_id как в запросе нет, то ручка вернет 404.
    """
    doc = load_json('revisions_without_details/revision_doc.json')
    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision',
        document=json.dumps(doc),
        created_at=dt.datetime.now(),
    )
    helpers.insert_default_mixins(pgsql, load_json)

    response = await taxi_eats_order_revision.put(
        '/v1/order-revision/customer-services/mixins/update?order_id=fake_id&',
        json=CUSTOMER_SERVICE_MIXINS_REQUEST,
    )

    assert response.status == 404
    assert (
        response.json()['message']
        == 'Revision with origin_id=fake_id does not exist'
    )
    assert response.json()['code'] == 'not found'


async def test_update_part_mixins(taxi_eats_order_revision, pgsql, load_json):
    """
    Тест проверяет частичное обновление таблицы миксинов.
    """
    doc = load_json('revisions_without_details/revision_doc.json')
    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision',
        document=json.dumps(doc),
        created_at=dt.datetime.now(),
    )

    request = {
        'customer_service_mixins': [
            {
                'customer_service_id': 'test_id_0',
                'mixins': [
                    {'discriminator_type': 'vat', 'value': 'nds_18'},
                    {
                        'discriminator_type': 'personal_tin_id',
                        'value': 'personal_tin_id_from_request',
                    },
                ],
            },
        ],
    }

    mixins = load_json('mixins.json')
    helpers.insert_revision_mixin(
        pgsql, 'test_order', 'test_id_0', json.dumps(mixins['mixins'][0]),
    )

    response = await taxi_eats_order_revision.put(
        MIXIN_UPDATE_HANDLER, json=request,
    )

    mixin = helpers.fetch_revision_mixin_payload(
        pgsql, 'test_order', 'test_id_0',
    )

    assert response.status == 200
    assert mixin['vat'] == 'nds_18'
    assert mixin['personal_tin_id'] == 'personal_tin_id_from_request'
    assert mixin['balance_client_id'] == 'test_balance_client_id'
