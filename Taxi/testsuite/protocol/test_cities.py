import pytest


@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_cities(
        taxi_protocol, load_json, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    def sort_by_city(obj):
        return sorted(obj, key=lambda x: x['city'])

    cards_response = taxi_protocol.post(
        '3.0/cities', headers={'Accept-Language': 'ru'},
    )
    assert cards_response.status_code == 200

    expected_result = load_json('response.json')
    assert sort_by_city(cards_response.json()) == sort_by_city(expected_result)
    assert dummy_choices.was_called() == use_choices_handler
