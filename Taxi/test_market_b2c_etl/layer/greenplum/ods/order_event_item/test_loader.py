import json

import market_b2c_etl.layer.greenplum.ods.checkouter.item_event.extractors as ex

TEST_JSON = """
{
    "id": 1078029727,
    "fromDate": "04-04-2021 07:47:20",
    "type": "ORDER_SUBSTATUS_UPDATED",
    "utc_event_processed": "04-04-2021 12:02:32",
    "synthetic_id": "123321",
    "orderBefore": {
        "id": 42074134,
        "items": [
            {
                "id": 81075241
            },
            {
                "id": 14257018
            }
        ]
    },
    "orderAfter": {
        "id": 42074134,
        "items": [
            {
                "id": 81075241
            }
        ],
        "creationDate": "16-04-2022 21:42:59"
    }
}
"""


def test_message_parse():
    actual_result = []
    for i in ex.transform_to_item_object(json.loads(TEST_JSON)):
        actual_result.append(i)
    assert len(actual_result) == 2
    assert actual_result[0]['is_deleted'] is False
    assert actual_result[1]['is_deleted'] is True
