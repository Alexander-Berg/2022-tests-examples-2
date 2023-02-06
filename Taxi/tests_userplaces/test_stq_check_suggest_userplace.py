import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='userplaces_suggest_params',
    consumers=['userplaces/userplaces'],
    clauses=[],
    is_config=True,
    default_value={
        'routehistory_max_size': 80,
        'min_dist_from_userplace': 200,
        'min_dist_from_completion_point': 2000,
        'min_near_points_size': 3,
        'max_weeks_count_from_ride': 12,
    },
)
@pytest.mark.translations(
    client_messages={
        'userplaces.suggest.short_text_rides_count': {
            'ru': '%(rides_count)s раз',
        },
        'userplaces.suggest.short_text_weeks_count': {
            'ru': ' за %(weeks_count)s недели',
        },
        'userplaces.suggest.full_text': {
            'ru': 'Вы были здесь уже %(rides_count)s раз',
        },
    },
)
@pytest.mark.now('2022-05-12T17:38:12.955+0000')
async def test_check_suggest_userplace(stq_runner, stq, load_json, mockserver):
    @mockserver.json_handler('/routehistory/routehistory/get')
    def _mock_routehistory(request):
        return load_json('routehistory_response.json')

    await stq_runner.check_suggest_userplace.call(
        task_id='new_counter',
        args=[
            'ade8868ce802195f81031651529931cf',
            '12345678901234567890123456789012',
            '02aaaaaaaaaaaaaaaaaaaa01',
            '400000000',
            'ru',
            [37.586634, 55.736716],
            'yataxi',
        ],
    )

    assert _mock_routehistory.times_called == 1
    assert stq.suggest_userplace.times_called == 1
    stq_args = stq.suggest_userplace.next_call()['kwargs']
    assert stq_args['order_id'] == 'ade8868ce802195f81031651529931cf'
    assert stq_args['user_id'] == '12345678901234567890123456789012'
    assert stq_args['locale'] == 'ru'
    assert stq_args['completion_point'] == [37.586634, 55.736716]
    assert stq_args['full_text'] == 'Вы были здесь уже 3 раз'
    assert stq_args['short_text'] == '3 раз за 2 недели'
    assert stq_args['available_types'] == ['home', 'other']
    assert stq_args['brand'] == 'yataxi'
