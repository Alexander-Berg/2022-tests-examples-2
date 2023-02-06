import datetime

import pytest

from taxi.util import locales

from eats_courier_scoring.common import entities
from eats_courier_scoring.common import startrek_punishment
from test_eats_courier_scoring import conftest
from test_eats_courier_scoring import consts


AVAILABLE_DEFECTS = [
    entities.DefectType(defect_type)
    for defect_type in consts.EATS_COURIER_SCORING_DEFECT_TYPES['defect_types']
]


@pytest.mark.parametrize(
    'found_defects',
    (
        AVAILABLE_DEFECTS,
        ['antilaw_courier', 'bad_courier', 'cancel_delay'],
        ['bad_courier'],
        [],
    ),
)
async def test_startrek(cron_context, found_defects):
    cron_context.config.EATS_COURIER_SCORING_DEFECT_TYPES = (
        consts.EATS_COURIER_SCORING_DEFECT_TYPES
    )
    cron_context.config.EATS_COURIER_SCORING_STARTREK_SETTINGS_BY_REGION = (
        consts.EATS_COURIER_SCORING_STARTREK_SETTINGS_BY_REGION
    )

    courier = entities.Courier(
        model=conftest.create_courier_model(1),
        defects=[
            entities.Defect(
                courier_id=1,
                order_id=1,
                order_nr=f'order_nr-{defect_type}',
                defect_type=defect_type,
                defect_dttm=datetime.datetime(2022, 4, 1),
                crm_comment='0',
                our_refund_total_lcy=0,
                incentive_refunds_lcy=0,
                incentive_rejected_order_lcy=0,
            )
            for defect_type in AVAILABLE_DEFECTS
        ],
        scores_by_defect_type={
            defect_name: int(defect_name in found_defects)
            for defect_name in AVAILABLE_DEFECTS
        },
    )
    startrek = startrek_punishment.StartrekPunishment(context=cron_context)
    result = startrek.formated_condition_for_defects(courier=courier)
    translations = cron_context.translations.eats_courier_scoring
    for defect_name in found_defects:
        assert f'order_nr-{defect_name}' in result
        translated_defect_description = translations.get_string_or_default(
            f'defect_descriptions.{defect_name}',
            locales.DEFAULT_LOCALE,
            None,
            defect_name,
        )
        assert translated_defect_description in result
    for defect_name in set(AVAILABLE_DEFECTS) - set(found_defects):
        assert f'order_nr-{defect_name}' not in result
