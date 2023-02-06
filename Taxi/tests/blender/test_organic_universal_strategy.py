from ctaxi_pyml.blender.v1 import (
    State,
    strategies,
    validate_blending,
    create_recommender,
)


def test_smoke(load):
    prev_state = State.from_json(load('request.json'))
    strategy = strategies.OrganicUniversal(
        strategies.OrganicUniversalConfig.from_json(load('config.json')),
    )

    next_state = strategy(prev_state)
    validate_blending(prev_state, next_state)
    assert len(next_state.grid.cells) != len(prev_state.grid.cells)


def test_with_mock_model(load, get_file_path):
    prev_state = State.from_json(load('request.json'))
    strategy = strategies.OrganicUniversal(
        strategies.OrganicUniversalConfig.from_json(
            load('config_with_predictions.json'),
        ),
        create_recommender(
            get_file_path('recommender_config.json'),
            'abcent_model.cbm',
            mock_mode=True,
        ),
    )

    next_state = strategy(prev_state)
    validate_blending(prev_state, next_state)
    assert len(next_state.grid.cells) != len(prev_state.grid.cells)
