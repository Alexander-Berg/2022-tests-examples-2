import pytest

from admin_orders.internal.order_sections import performers


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'performer_dict,expected_result',
    [
        # case with necessary fields
        (
            {
                'id': 'id1',
                'name': 'some name',
                'score': 5,
                'tags': ['tag1', 'tag2'],
                'phone_pd_ids': ['phone_pd_id_1'],
                'email_pd_ids': ['email_pd_id_1'],
            },
            {
                'performer_id': 'id1',
                'name': 'some name',
                'score': 5,
                'tags': ['tag1', 'tag2'],
                'phone_pd_ids': ['phone_pd_id_1'],
                'email_pd_ids': ['email_pd_id_1'],
            },
        ),
        # case with missing fields
        (
            {
                'id': 'id2',
                'score': 2,
                'tags': ['tag3', 'tag4'],
                'phone_pd_ids': ['phone_pd_id_2'],
            },
            {
                'performer_id': 'id2',
                'score': 2,
                'tags': ['tag3', 'tag4'],
                'phone_pd_ids': ['phone_pd_id_2'],
            },
        ),
    ],
)
def test_extract_discount_data(performer_dict, expected_result):
    result = performers.get_fields_from_performer(performer_dict)
    assert result == expected_result
