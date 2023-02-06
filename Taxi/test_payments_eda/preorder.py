import uuid

import pytest

from test_payments_eda import consts


# Needs to distinguish value `None` and null (no any value).
NO_CARD_ID = 'no-card-id'

GROCERY_TRUST_SETTINGS = pytest.mark.config(
    PAYMENTS_EDA_GROCERY_TRUST_SERVICE_SETTINGS={
        'by_iso2': [
            {
                'code': 'RU',
                'billing_service': 'lavka_courier_payment',
                'product_id': 'lavka_courier',
            },
            {
                'code': 'RU_settings-version',
                'billing_service': 'lavka_courier_payment_versioned',
                'product_id': 'lavka_courier_versioned',
            },
        ],
    },
)

ISRAEL_BILLING_SERVICE = 'isr-billing-service'
ISRAEL_PRODUCT_ID = 'isr-product-id'

GROCERY_TRUST_SETTINGS_ISRAEL = pytest.mark.config(
    PAYMENTS_EDA_GROCERY_TRUST_SERVICE_SETTINGS={
        'by_iso2': [
            {
                'code': 'IL',
                'billing_service': ISRAEL_BILLING_SERVICE,
                'product_id': ISRAEL_PRODUCT_ID,
            },
        ],
    },
)

PARAMETRIZE_EDA_AND_GROCERY_ORDER = pytest.mark.parametrize(
    'is_grocery,external_ref',
    [(True, 'bfd7526fa5d74eae9e5c034d40235be0-grocery'), (False, '123')],
)

GROCERY_TRUST_SERVICE_ENABLED_DISABLED = pytest.mark.parametrize(
    'grocery_billing_service,grocery_product_id,'
    'grocery_trust_settings_enabled',
    [
        pytest.param(
            'lavka_courier_payment',
            'lavka_courier',
            True,
            marks=pytest.mark.config(
                PAYMENTS_EDA_GROCERY_TRUST_SERVICE_ENABLED=True,
            ),
        ),
        pytest.param(
            'food_payment',
            'eda_61664402_ride',
            False,
            marks=pytest.mark.config(
                PAYMENTS_EDA_GROCERY_TRUST_SERVICE_ENABLED=False,
            ),
        ),
    ],
)

GROCERY_DEFAULT_TIN = '9718101499'


def grocery_orders_response_body(
        country_iso2='RU',
        grocery_billing_flow='payments_eda',
        billing_settings_version=None,
):
    json = {
        'cart_id': '11b51da9-04e9-40dd-a51c-b4f712b24a63',
        'cart_version': 1,
        'country_iso2': country_iso2,
        'created': '2020-03-10T00:00:00+00:00',
        'due': '2020-03-10T01:00:00+00:00',
        'idempotency_token': '6b9c7ad9-ce99-4df8-808e-835c5d7184ad',
        'location': consts.LOCATION,
        'offer_id': 'offer-id',
        'order_id': 'bf2431b9-de4e-45ca-8ee5-ef11f10411ac',
        'order_version': 0,
        'region_id': 123,
        'status': 'draft',
        'depot': {'id': '2809', 'tin': GROCERY_DEFAULT_TIN},
        'billing_flow': grocery_billing_flow,
        'country': 'Russia',
        'user_info': {},
        'receipts': [],
        # TODO Delete after https://st.yandex-team.ru/LAVKABACKEND-7906
        'items': [],
    }
    if billing_settings_version is not None:
        json['billing_settings_version'] = billing_settings_version

    return json


def _add_required_payment(mock_grocery_cart, card_id=None, make_random=False):
    if make_random:
        meta_info_card_id = str(uuid.uuid4())
    else:
        meta_info_card_id = card_id
    mock_grocery_cart.set_payment_method(meta_info_card_id)


def _add_card_ids(eda_response, card_id=None, make_random=False):
    for i, item in enumerate(eda_response['items']):
        # This metadata key should force us to allow only this payment type.
        if make_random:
            meta_info_card_id = 'generated_card_id_%d.' % i
        else:
            meta_info_card_id = card_id
        item['meta_info'] = {
            'payment_method': {'type': 'card', 'id': meta_info_card_id},
        }


def eats_response_body(
        item_id,
        currency,
        amount,
        business='store',
        items=None,
        country_iso2='RU',
):
    items_ret = [{'amount': amount, 'currency': currency, 'item_id': item_id}]
    if items is not None:
        items_ret = items
    eats_response = {
        'location': consts.LOCATION,
        'items': items_ret,
        'country_code': country_iso2,
        'region_id': 123,
        'uuid': consts.DEFAULT_YANDEX_UID,
        'service_product_id': 'eda_107819207_ride',
    }
    if business is not None:
        eats_response['business'] = business
    return eats_response


def mock_get_order_helper(
        grocery_orders_mockserver,
        mock_grocery_cart,
        eda_doc_mockserver,
        is_grocery=False,
        item_id='123',
        currency='RUB',
        amount='10.50',
        card_id=NO_CARD_ID,
        make_random=False,
        items=None,
        business=None,
        country_iso2='RU',
        base_url=None,
        grocery_billing_flow='payments_eda',
        billing_settings_version=None,
):
    if is_grocery:
        grocery_response = grocery_orders_response_body(
            country_iso2=country_iso2,
            grocery_billing_flow=grocery_billing_flow,
            billing_settings_version=billing_settings_version,
        )
        mock_grocery_cart.set_items(item_id, amount, currency)
        if card_id != NO_CARD_ID:  # look to |NO_CARD_ID| comment.
            _add_required_payment(
                mock_grocery_cart, card_id=card_id, make_random=make_random,
            )
        return grocery_orders_mockserver(grocery_response)

    eda_response = eats_response_body(
        item_id,
        currency,
        amount,
        business=business,
        items=items,
        country_iso2=country_iso2,
    )
    if card_id != NO_CARD_ID:  # look to |NO_CARD_ID| comment.
        _add_card_ids(eda_response, card_id=card_id, make_random=make_random)
    return eda_doc_mockserver(eda_response, base_url)
