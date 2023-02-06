# pylint: disable=W0612,R1705
import typing

import pytest

ORDER_NR = 'dummy_order'


@pytest.fixture(name='external_services_empty_mock', autouse=True)
def _order_statuses_mock(mockserver):
    @mockserver.json_handler('/eats-vendor/api/v1/server/orders/statuses')
    def _order_statuses_mock(request):
        return {'orders': []}

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1' '/order-revision/list',
    )
    def eats_core_order_revision_list(request):
        return {'order_id': ORDER_NR, 'revisions': []}

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1'
        '/order-revision/customer-services/details',  # pylint: disable=C0103
    )
    def order_revision_customer_services(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _catalog_storage_brand_id(request):
        return {
            'places': [
                {
                    'id': 1,
                    'name': 'MacDonald`s на Киевской',
                    'brand': {
                        'id': 123,
                        'slug': 'Mac',
                        'name': 'MacDonald`s',
                        'picture_scale_type': 'aspect_fit',
                    },
                    'revision_id': 1,
                    'updated_at': '2020-04-28T12:00:00+03:00',
                },
            ],
            'not_found_place_ids': [],
        }


def order_event_payload(order_event: str) -> dict:
    payload = {'order_nr': ORDER_NR, 'order_event': order_event}
    if order_event == 'created':
        payload['order_type'] = 'eda'
        payload['created_at'] = '2020-09-04T15:26:43+00:00'
        payload['place_id'] = '1'
    elif order_event == 'confirmed':
        payload['confirmed_at'] = '2020-09-04T15:26:51+00:00'
    elif order_event == 'finished':
        payload['finished_at'] = '2020-09-04T15:59:51+00:00'
    elif order_event == 'cancelled':
        payload['cancellation_reason'] = 'not_ready'
    return payload


def order_subjects_payload(order_event, weight=None, statuses=None):
    if order_event == 'created':
        payload = {
            'id': {'id': ORDER_NR, 'type': 'order'},
            'factors': [
                {'name': 'order_type', 'type': 'string', 'value': 'eda'},
                {
                    'name': 'created_at',
                    'type': 'datetime',
                    'value': '2020-09-04T15:26:43+00:00',
                },
                {'name': 'brand_id', 'type': 'string', 'value': '123'},
                {
                    'name': 'brand_name',
                    'type': 'string',
                    'value': 'MacDonald`s',
                },
                {'name': 'place_id', 'type': 'string', 'value': '1'},
                {
                    'name': 'place_name',
                    'type': 'string',
                    'value': 'MacDonald`s на Киевской',
                },
            ],
        }
        if weight:
            payload['factors'].append(
                {'name': 'weight', 'type': 'int', 'value': weight},
            )
        return payload
    elif order_event == 'finished':
        payload = {
            'id': {'id': ORDER_NR, 'type': 'order'},
            'factors': [
                {
                    'name': 'finished_at',
                    'type': 'datetime',
                    'value': '2020-09-04T15:59:51+00:00',
                },
            ],
        }
        if weight:
            payload['factors'].append(
                {'name': 'weight', 'type': 'int', 'value': weight},
            )
        if statuses:
            for status in statuses:
                payload['factors'].append(
                    {
                        'name': status['name'],
                        'type': 'datetime',
                        'value': status['value'],
                    },
                )
        return payload
    return {}


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_all_factors.sql'],
)
@pytest.mark.parametrize(
    'event_payload,expected_subjects_request',
    [
        (
            order_event_payload('created'),
            {
                'id': {'id': ORDER_NR, 'type': 'order'},
                'factors': [
                    {'name': 'order_type', 'type': 'string', 'value': 'eda'},
                    {
                        'name': 'created_at',
                        'type': 'datetime',
                        'value': '2020-09-04T15:26:43+00:00',
                    },
                    {'name': 'brand_id', 'type': 'string', 'value': '123'},
                    {
                        'name': 'brand_name',
                        'type': 'string',
                        'value': 'MacDonald`s',
                    },
                    {'name': 'place_id', 'type': 'string', 'value': '1'},
                    {
                        'name': 'place_name',
                        'type': 'string',
                        'value': 'MacDonald`s на Киевской',
                    },
                ],
            },
        ),
        (
            order_event_payload('confirmed'),
            {
                'id': {'id': ORDER_NR, 'type': 'order'},
                'factors': [
                    {
                        'name': 'confirmed_at',
                        'type': 'datetime',
                        'value': '2020-09-04T15:26:51+00:00',
                    },
                ],
            },
        ),
        (
            order_event_payload('finished'),
            {
                'id': {'id': ORDER_NR, 'type': 'order'},
                'factors': [
                    {
                        'name': 'finished_at',
                        'type': 'datetime',
                        'value': '2020-09-04T15:59:51+00:00',
                    },
                ],
            },
        ),
        (
            order_event_payload('cancelled'),
            {
                'id': {'id': ORDER_NR, 'type': 'order'},
                'factors': [
                    {
                        'name': 'cancel_reason',
                        'type': 'string',
                        'value': 'not_ready',
                    },
                ],
            },
        ),
    ],
)
async def test_stq_handler_order_client(
        stq_runner, testpoint, event_payload, expected_subjects_request,
):
    @testpoint('test_subject_request')
    def test_subject(data):
        data['factors'] = sorted(data['factors'], key=lambda x: x['name'])
        expected_subjects_request['factors'] = sorted(
            expected_subjects_request['factors'], key=lambda x: x['name'],
        )
        assert data == expected_subjects_request

    await stq_runner.eats_logistics_performer_payouts_client_order_payload.call(  # noqa: E501
        task_id='dummy_task', kwargs=event_payload,
    )

    assert test_subject.times_called == 1


class Product:
    def __init__(self, weight=None, gram_weight=None):
        self.weight = weight
        self.gram_weight = gram_weight

    def payload(self):
        payload = {
            'id': 'product_id',
            'name': 'product 1 (Category 1)',
            'partner_name': 'product 1 (Category 1)',
            'cost_for_customer': '110',
            'type': 'product',
            'vat': 'nds_20',
        }
        if self.weight:
            payload['weight'] = self.weight
        if self.gram_weight:
            payload['gram_weight'] = self.gram_weight
        return payload


class CustomerServices:
    def __init__(self, products: typing.List[Product]):
        self.products = products

    def payload(self):
        payload = {
            'revision_id': 'revision2',
            'created_at': '2021-10-13T15:35:43+00:00',
            'customer_services': [
                {
                    'id': 'composition-products',
                    'name': 'Продукты заказа',
                    'cost_for_customer': '110',
                    'currency': 'RUB',
                    'type': 'composition_products',
                    'trust_product_id': 'eda_107819207_ride',
                    'place_id': '475529',
                    'personal_tin_id': '05fcebe0a0db43e8bf963eaed35efd8f',
                    'balance_client_id': '4294491982',
                    'details': {
                        'composition_products': [],
                        'discriminator_type': 'composition_products_details',
                    },
                },
            ],
        }

        for product in self.products:
            payload['customer_services'][0]['details'][
                'composition_products'
            ].append(product.payload())

        return payload


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_all_factors.sql'],
)
@pytest.mark.parametrize(
    'order_event,core_revision_list_status,expected_subjects_times_called',
    [
        ('created', 400, 1),
        ('created', 403, 1),
        ('created', 404, 1),
        ('created', 500, 0),
        ('finished', 400, 1),
        ('finished', 403, 1),
        ('finished', 404, 1),
        ('finished', 500, 0),
    ],
)
async def test_order_weight_factor_failed_revision_list_request(
        mockserver,
        stq_runner,
        testpoint,
        order_event,
        core_revision_list_status,
        expected_subjects_times_called,
):
    @testpoint('test_subject_request')
    def test_subject(data):
        data['factors'] = sorted(data['factors'], key=lambda x: x['name'])
        expected_subjects_request = order_subjects_payload(order_event)
        expected_subjects_request['factors'] = sorted(
            expected_subjects_request['factors'], key=lambda x: x['name'],
        )
        assert data == expected_subjects_request

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1' '/order-revision/list',
    )
    def eats_core_order_revision_list(request):
        return mockserver.make_response(
            status=core_revision_list_status, json={},
        )

    await stq_runner.eats_logistics_performer_payouts_client_order_payload.call(  # noqa: E501
        task_id='dummy_task',
        kwargs=order_event_payload(order_event),
        expect_fail=(expected_subjects_times_called == 0),
    )
    assert test_subject.times_called == expected_subjects_times_called


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_all_factors.sql'],
)
@pytest.mark.parametrize(
    'order_event,core_revision_details_status,expected_subjects_times_called',
    [
        ('created', 400, 1),
        ('created', 403, 1),
        ('created', 404, 1),
        ('created', 500, 0),
        ('finished', 400, 1),
        ('finished', 403, 1),
        ('finished', 404, 1),
        ('finished', 500, 0),
    ],
)
async def test_order_weight_factor_failed_revision_customer_services_request(
        mockserver,
        stq_runner,
        testpoint,
        order_event,
        core_revision_details_status,
        expected_subjects_times_called,
):
    @testpoint('test_subject_request')
    def test_subject(data):
        data['factors'] = sorted(data['factors'], key=lambda x: x['name'])
        expected_subjects_request = order_subjects_payload(order_event)
        expected_subjects_request['factors'] = sorted(
            expected_subjects_request['factors'], key=lambda x: x['name'],
        )
        assert data == expected_subjects_request

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1' '/order-revision/list',
    )
    def eats_core_order_revision_list(request):
        return mockserver.make_response(
            status=200,
            json={
                'order_id': ORDER_NR,
                'revisions': [
                    {'revision_id': 'revision1'},
                    {'revision_id': 'revision2'},
                ],
            },
        )

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1'
        '/order-revision/customer-services/details',  # pylint: disable=C0103
    )
    def order_revision_customer_services(request):
        return mockserver.make_response(
            status=core_revision_details_status, json={},
        )

    await stq_runner.eats_logistics_performer_payouts_client_order_payload.call(  # noqa: E501
        task_id='dummy_task',
        kwargs=order_event_payload(order_event),
        expect_fail=(expected_subjects_times_called == 0),
    )
    assert test_subject.times_called == expected_subjects_times_called


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_all_factors.sql'],
)
@pytest.mark.parametrize(
    'order_event,core_revision_details_response,expected_order_weight',
    [
        ('created', CustomerServices([Product({}, 1000)]).payload(), 1000),
        ('finished', CustomerServices([Product({}, 1000)]).payload(), 1000),
        (
            'created',
            CustomerServices(
                [Product({'value': 1500, 'measure_unit': 'GRM'}, 1000)],
            ).payload(),
            1500,
        ),
        (
            'finished',
            CustomerServices(
                [Product({'value': 1500, 'measure_unit': 'GRM'}, 1000)],
            ).payload(),
            1500,
        ),
        (
            'created',
            CustomerServices(
                [
                    Product({'value': 1500, 'measure_unit': 'GRM'}, 1000),
                    Product({'value': 200, 'measure_unit': 'MLT'}, None),
                    Product({}, 300),
                    Product({'value': 100, 'measure_unit': 'UNKNOWN'}, None),
                ],
            ).payload(),
            2000,
        ),
        (
            'finished',
            CustomerServices(
                [
                    Product({'value': 1500, 'measure_unit': 'GRM'}, 1000),
                    Product({'value': 200, 'measure_unit': 'MLT'}, None),
                    Product({}, 300),
                    Product({'value': 100, 'measure_unit': 'UNKNOWN'}, None),
                ],
            ).payload(),
            2000,
        ),
    ],
)
async def test_get_order_weight(
        mockserver,
        stq_runner,
        testpoint,
        order_event,
        core_revision_details_response,
        expected_order_weight,
):
    @testpoint('test_subject_request')
    def test_subject(data):
        data['factors'] = sorted(data['factors'], key=lambda x: x['name'])
        expected_subjects_request = order_subjects_payload(
            order_event, expected_order_weight,
        )
        expected_subjects_request['factors'] = sorted(
            expected_subjects_request['factors'], key=lambda x: x['name'],
        )
        assert data == expected_subjects_request

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1' '/order-revision/list',
    )
    def eats_core_order_revision_list(request):
        return mockserver.make_response(
            status=200,
            json={
                'order_id': ORDER_NR,
                'revisions': [
                    {'revision_id': 'revision1'},
                    {'revision_id': 'revision2'},
                ],
            },
        )

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1'
        '/order-revision/customer-services/details',  # pylint: disable=C0103
    )
    def order_revision_customer_services(request):
        return mockserver.make_response(
            status=200, json=core_revision_details_response,
        )

    await stq_runner.eats_logistics_performer_payouts_client_order_payload.call(  # noqa: E501
        task_id='dummy_task', kwargs=order_event_payload(order_event),
    )

    assert test_subject.times_called == 1


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_all_factors.sql'],
)
@pytest.mark.parametrize(
    'order_event,vendor_order_statuses_response,expected_order_statuses',
    [
        ('finished', [], []),
        (
            'finished',
            [
                {
                    'status': 'ready',
                    'initiator': 'dummy',
                    'created_at': '2020-09-04T16:26:43+00:00',
                },
                {
                    'status': 'released',
                    'initiator': 'dummy',
                    'created_at': '2020-09-04T17:27:43+00:00',
                },
                {
                    'status': 'new',
                    'initiator': 'dummy',
                    'created_at': '2020-09-04T18:28:43+00:00',
                },
                {
                    'status': 'given',
                    'initiator': 'dummy',
                    'created_at': '2020-09-04T19:29:43+00:00',
                },
            ],
            [
                {
                    'name': 'package_ready_at',
                    'value': '2020-09-04T16:26:43+00:00',
                },
                {
                    'name': 'package_given_at',
                    'value': '2020-09-04T17:27:43+00:00',
                },
                {
                    'name': 'package_accepted_at',
                    'value': '2020-09-04T18:28:43+00:00',
                },
            ],
        ),
    ],
)
async def test_get_order_statuses(
        mockserver,
        stq_runner,
        testpoint,
        order_event,
        vendor_order_statuses_response,
        expected_order_statuses,
):
    @testpoint('test_subject_request')
    def test_subject(data):
        data['factors'] = sorted(data['factors'], key=lambda x: x['name'])
        expected_subjects_request = order_subjects_payload(
            order_event, None, expected_order_statuses,
        )
        expected_subjects_request['factors'] = sorted(
            expected_subjects_request['factors'], key=lambda x: x['name'],
        )
        assert data == expected_subjects_request

    @mockserver.json_handler('/eats-vendor/api/v1/server/orders/statuses')
    def _order_statuses_mock(request):
        return {
            'orders': [
                {
                    'order_nr': ORDER_NR,
                    'statuses': vendor_order_statuses_response,
                },
            ],
        }

    await stq_runner.eats_logistics_performer_payouts_client_order_payload.call(  # noqa: E501
        task_id='dummy_task', kwargs=order_event_payload(order_event),
    )

    assert test_subject.times_called == 1
