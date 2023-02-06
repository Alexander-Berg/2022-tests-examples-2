from eats_courier_scoring.common import entities
from eats_courier_scoring.common import experiments
from test_eats_courier_scoring import conftest


DEFECT_SCORES = [
    {
        'defect_type': 'fake_gps',
        'scores': [
            {
                'thresholds_share': {'from': 0},
                'score': 10,
                'thresholds_absolute': {'from': 3},
            },
            {'score': 5},
        ],
    },
]


@conftest.create_exp3_response(
    courier_id=1,
    enabled=True,
    punishment_names=['name_1', 'name_2'],
    defect_scores=DEFECT_SCORES,
)
@conftest.create_exp3_response(
    courier_id=2,
    enabled=True,
    punishment_names=['name_3'],
    defect_scores=DEFECT_SCORES,
)
@conftest.create_exp3_response(
    courier_id=3,
    enabled=False,
    punishment_names=['name_1'],
    defect_scores=DEFECT_SCORES,
)
async def test_get_experiment_couriers(cron_context):
    defect_scores = {
        entities.DefectType('fake_gps'): [
            experiments.DefectScore(
                score=10,
                thresholds_absolute=(3, float('inf')),
                thresholds_share=(0, 1),
            ),
            experiments.DefectScore(
                score=5,
                thresholds_absolute=(0, float('inf')),
                thresholds_share=(0, 1),
            ),
        ],
    }

    expected = {
        1: experiments.DefectsScoringConfigResult(
            enabled=True,
            punishment_names={'name_1', 'name_2'},
            defect_scores=defect_scores,
        ),
        2: experiments.DefectsScoringConfigResult(
            enabled=True,
            punishment_names={'name_3'},
            defect_scores=defect_scores,
        ),
        3: experiments.DefectsScoringConfigResult(
            enabled=False,
            punishment_names={'name_1'},
            defect_scores=defect_scores,
        ),
        1000: experiments.DefectsScoringConfigResult(
            enabled=False, punishment_names=set(), defect_scores=dict(),
        ),
    }
    result = await experiments.get_couriers_scoring_config(
        cron_context,
        couriers=[
            entities.Courier(
                model=conftest.create_courier_model(1), defects=[],
            ),
            entities.Courier(
                model=conftest.create_courier_model(2), defects=[],
            ),
            entities.Courier(
                model=conftest.create_courier_model(3), defects=[],
            ),
            entities.Courier(
                model=conftest.create_courier_model(1000), defects=[],
            ),
        ],
    )

    assert result == expected
