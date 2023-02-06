from taxi_pyml.common.support_base import business_rules
from taxi_pyml.common.support_base import text_simirality


def test_config(load_json):
    blocklist = load_json('resources/black_list_config.json')
    config = business_rules.Config(
        load_json('resources/eats_support_config.json'),
    )

    taste1, taste2 = config.get_macros_for_topic('Вкус')
    assert taste1.actions[0] == {
        'action': 'close',
        'arguments': {'macro_id': 1},
    }
    assert taste2.actions[0] == {'action': 'dismiss', 'arguments': {}}
    temp1, temp2 = config.get_macros_for_topic('Температура')
    assert temp1.frequency == 1
    assert temp2.frequency == 1

    time_problem_request = load_json('time_problem_request.json')

    assert config.sample_macro_from_empirical_distribution([]) is None
    assert (
        config.sample_macro_from_empirical_distribution(
            [
                business_rules.Macro.from_dict(
                    {
                        'actions': [
                            {'action': 'close', 'arguments': {'macro_id': 1}},
                        ],
                        'frequency': 1,
                        'status': 'ok',
                        'rules': [],
                    },
                ),
            ],
        ).status
        == 'ok'
    )

    macros = config.get_macros_for_topic('Время')
    assert macros[0].actions[0]['arguments']['macro_id'] == 2
    assert macros[1].actions[0]['action'] == 'dismiss'

    assert (
        config.choose_from_macros(
            config.get_macros_for_topic('Время'),
            business_rules.flat_dict(time_problem_request, '__'),
        )[0].actions[0]['arguments']['macro_id']
        == 2
    )

    config = business_rules.Config(
        load_json('resources/taxi_support_config.json'),
    )

    macros = config.get_macros_for_topic('rd_fare_cancel_driver_canceled')
    assert macros[0].actions[0]['arguments']['macro_id'] == 49180
    assert macros[1].actions[0]['arguments']['macro_id'] == 49181
    assert macros[2].actions[0]['arguments']['macro_id'] == 49182
    assert (
        config.choose_from_macros(
            [
                macro
                for macro in macros
                if not config.has_blocklist_macro(macro, blocklist['macros'])
            ],
            load_json('driver_cancel_request.json'),
        )[0].actions[0]['arguments']['macro_id']
        == 49181
    )


def test_text_similarity():
    similarity_meter = text_simirality.SimilarityMeter('levenshtein_distance')
    assert similarity_meter('planet', 'planetary') == 3
    assert similarity_meter('', 'planetary') == 9
    assert similarity_meter('book', 'back') == 2
    assert similarity_meter('book', 'book') == 0
    assert similarity_meter('book', 'brook') == 1
    similarity_meter = text_simirality.SimilarityMeter(
        'levenshtein_similarity',
    )
    assert similarity_meter('planet', 'planetar') == 0.75
    assert similarity_meter('', 'planetary') == 0
    assert similarity_meter('book', 'back') == 0.5
    assert similarity_meter('book', 'book') == 1
    assert similarity_meter('book', 'brook') == 0.8
