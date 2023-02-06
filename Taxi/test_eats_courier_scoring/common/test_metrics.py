import datetime

from eats_courier_scoring.common import entities
from eats_courier_scoring.common import metrics
from test_eats_courier_scoring import conftest

NOW = datetime.datetime.utcnow()


def test_empty_defects():
    """Check metric is created if courier with no defects."""
    punishment = entities.Punishment(
        id=1,
        courier_id=1,
        punishment_type=entities.PunishmentType.COMMUNICATION,
        punishment_name='communication',
        arguments={},
        is_sent=True,
        created_at=NOW,
        region_name='region',
    )
    metrics.create_punishment_metric(
        punishment=punishment,
        courier=entities.Courier(
            model=conftest.create_courier_model(courier_id=1),
            scores_by_defect_type={},
            defects=[],
        ),
    )
