import json
import market_b2c_etl.layer.greenplum.ods.checkouter.order_promo_event.extractors as ex

TEST_JSON = """
{
    "id": 1078029727,
    "fromDate": "04-04-2021 07:47:20",
    "orderAfter": {
        "id": 42074134,
        "promos": [
            {
                "bundleReturnRestrict": false,
                "buyerItemsDiscount": 90,
                "coinId": 1171112842,
                "deliveryDiscount": 0,
                "marketPromoId": "pnkDYGnhP2GQSloC1MTnIQ",
                "shopPromoId": "#8611",
                "subsidy": 90,
                "type": "MARKET_PROMOCODE"
            },
            {
                "bundleReturnRestrict": false,
                "buyerItemsDiscount": 0,
                "deliveryDiscount": 0,
                "marketPromoId": "FiK3voCGRr6dz3JJ2Yr_NA",
                "subsidy": 0,
                "type": "CASHBACK"
            },
            {
                "anaplanId": "a900e8225f1748cd9026b50d8d0b8df8",
                "bundleReturnRestrict": false,
                "buyerItemsDiscount": 60,
                "deliveryDiscount": 0,
                "marketPromoId": "nTZUaHQ4GKFsZs985rY2yw",
                "shopPromoId": "a900e8225f1748cd9026b50d8d0b8df8",
                "subsidy": 60,
                "type": "DIRECT_DISCOUNT"
            }
        ]
    }
}
"""


def test_message_parse():
    actual_result = []
    for i in ex.get_order_promo_events_raw(json.loads(TEST_JSON)):
        actual_result.append(i)
    assert len(actual_result) == 3
