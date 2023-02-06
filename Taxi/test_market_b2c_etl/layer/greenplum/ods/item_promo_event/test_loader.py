import json

import market_b2c_etl.layer.greenplum.ods.checkouter.item_promo_event.extractors as ex

TEST_JSON = """
{
    "id": 1078029727,
    "fromDate": "04-04-2021 07:47:20",
    "orderBefore": {
        "id": 42074134,
        "items": [
            {
                "id": 81075241,
                "promos":
                [
                    {
                        "bundleReturnRestrict": false,
                        "buyerDiscount": 0,
                        "buyerSubsidy": 0,
                        "cashbackAccrualAmount": 4,
                        "marketPromoId": "t6cfZWcMa8QwEDA8qnIXXA",
                        "subsidy": 0,
                        "type": "CASHBACK"
                    },
                    {
                        "bundleReturnRestrict": false,
                        "buyerDiscount": 0,
                        "buyerSubsidy": 0,
                        "cashbackAccrualAmount": 31,
                        "marketPromoId": "H7fsY_KXKsRibVu58IZsaQ",
                        "subsidy": 0,
                        "type": "CASHBACK"
                    },
                    {
                        "bundleReturnRestrict": false,
                        "buyerDiscount": 745,
                        "buyerSubsidy": 0,
                        "marketPromoId": "",
                        "subsidy": 0,
                        "type": "MARKET_BLUE"
                    }
                ]
            },
            {
                "id": 14257018,
                "promos":
                [
                    {
                        "bundleReturnRestrict": false,
                        "buyerDiscount": 48,
                        "buyerSubsidy": 0,
                        "marketPromoId": "eS3XdDNjFMPCegS7Jgzyzw",
                        "subsidy": 0,
                        "type": "MARKET_COUPON"
                    }
                ]
            }
        ]
    },
    "orderAfter": {
        "id": 42074134,
        "items": [
            {
                "id": 81075241,
                "promos":
                [
                    {
                        "bundleReturnRestrict": false,
                        "buyerDiscount": 0,
                        "buyerSubsidy": 0,
                        "cashbackAccrualAmount": 4,
                        "marketPromoId": "t6cfZWcMa8QwEDA8qnIXXA",
                        "subsidy": 0,
                        "type": "CASHBACK"
                    },
                    {
                        "bundleReturnRestrict": false,
                        "buyerDiscount": 0,
                        "buyerSubsidy": 0,
                        "cashbackAccrualAmount": 31,
                        "marketPromoId": "H7fsY_KXKsRibVu58IZsaQ",
                        "subsidy": 0,
                        "type": "CASHBACK"
                    },
                    {
                        "bundleReturnRestrict": false,
                        "buyerDiscount": 745,
                        "buyerSubsidy": 0,
                        "marketPromoId": "",
                        "subsidy": 0,
                        "type": "MARKET_BLUE"
                    }
                ]
            }
        ]
    }
}
"""


def test_message_parse():
    actual_result = []
    for i in ex.get_item_promo_events_raw(json.loads(TEST_JSON)):
        actual_result.append(i)
    assert len(actual_result) == 4
    assert actual_result[0]['is_deleted'] is False
    assert actual_result[1]['is_deleted'] is False
    assert actual_result[2]['is_deleted'] is False
    assert actual_result[3]['is_deleted'] is True
