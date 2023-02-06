import pytest

from taxi.internal import dbh


@pytest.mark.parametrize('resize_doc,expected_result', [
    ({}, True),
    ({'ride_sum_delta': 0, 'tips_sum_delta': 0}, True),
    ({'tips_sum_delta': 0}, True),
    ({'ride_sum_delta': 0}, True),
    ({'tips_sum_delta': 1}, False),
    ({'ride_sum_delta': 1}, False),
    ({'ride_sum_delta': 1, 'tips_sum_delta': 0}, False),
    ({'ride_sum_delta': 0, 'tips_sum_delta': 1}, False),
    ({'ride_sum_delta': 1, 'tips_sum_delta': 1}, False),
])
def test_delta_is_zero(resize_doc, expected_result):
    resize = dbh.taximeter_balance_changes.Doc(resize_doc)
    assert resize.delta_is_zero == expected_result


@pytest.mark.filldb
@pytest.inline_callbacks
def test_get_latest_payments():
    payment_id_type_and_expected_doc = [
        # (trust payment ID, payment type, expected doc)
        ('no_resizes', dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE, None),
        (
            'single_resize',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Doc({
                '_id': 'single_resize_1',
                'trust_payment_id': 'single_resize',
                'payment_type': (
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
                ),
                'sequence_number': 1,
            }),
        ),
        (
            'two_resizes',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Doc({
                '_id': 'two_resizes_2',
                'trust_payment_id': 'two_resizes',
                'payment_type': (
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
                ),
                'sequence_number': 2,
            }),
        ),
        (
            'four_resizes',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Doc({
                '_id': 'four_resizes_4',
                'trust_payment_id': 'four_resizes',
                'payment_type': (
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
                ),
                'sequence_number': 4,
            }),
        ),
    ]
    trust_payment_ids = [item[0] for item in payment_id_type_and_expected_doc]
    payments_by_trust_payment_id_and_type, _ = yield (
        dbh.taximeter_balance_changes.Doc.get_latest_payments(trust_payment_ids)
    )
    for item in payment_id_type_and_expected_doc:
        trust_payment_id, payment_type, expected_doc = item
        payment_doc = payments_by_trust_payment_id_and_type.get(
            (trust_payment_id, payment_type)
        )
        assert payment_doc == expected_doc
