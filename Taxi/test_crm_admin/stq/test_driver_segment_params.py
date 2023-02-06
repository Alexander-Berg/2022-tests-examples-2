from crm_admin.utils.segment import driver_segment_params


def test_get_driver_segment_config():
    class Field:
        def __init__(self, field_id, value):
            self.field_id = field_id
            self.value = value

    class Campaign:
        settings = [
            Field('executor_type', 'driver'),
            Field('app', 'some app'),
            Field('tag_ccode', ['tag1', 'tag2']),
            Field('exclude_tag_ccode', ['tag3', 'tag4']),
            Field('rating_from', 3),
            Field('rating_to', 3),
            Field(
                'g_car_model',
                [
                    [Field('car_brand', 'A'), Field('car_model', 'a')],
                    [Field('car_brand', 'B')],
                ],
            ),
            Field('extra_fields', ['a', 'b']),
        ]

    campaign = Campaign()

    conf = driver_segment_params.get_driver_segment_config(campaign)

    expected = {
        'filters': {
            'tags': {
                'include': {'ccode': ['tag1', 'tag2']},
                'exclude': {'ccode': ['tag3', 'tag4']},
            },
            'profile': {
                'rating': {'from': 3, 'to': 3},
                'car_model': [{'brand': 'A', 'model': 'a'}, {'brand': 'B'}],
            },
            'properties': {'executor_type': 'driver', 'app': 'some app'},
        },
        'extra_fields': ['a', 'b'],
    }
    assert conf == expected
