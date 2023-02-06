# pylint: disable=protected-access
import typing

import pytest

from eats_courier_scoring.common import courier_wall
from eats_courier_scoring.common import entities
from test_eats_courier_scoring import conftest
from test_eats_courier_scoring import consts

COURIER = entities.Courier(
    model=conftest.create_courier_model(1),
    defects=[
        conftest.create_defect(
            1, 1, defect_type=entities.DefectType('damaged_order'),
        ),
        conftest.create_defect(
            1, 1, defect_type=entities.DefectType('mismatch_orders'),
        ),
    ],
    scores_by_defect_type={entities.DefectType('damaged_order'): 1.0},
)


def generate_template_kwargs() -> typing.Set[str]:
    available_defect_kwargs = courier_wall._generate_available_defect_kwargs(
        consts.EATS_COURIER_SCORING_DEFECT_TYPES,
    )
    available_score_defects_kwargs = (
        courier_wall._generate_available_score_defects_kwargs(
            consts.EATS_COURIER_SCORING_DEFECT_TYPES,
        )
    )

    return courier_wall._generate_available_template_kwargs_names(
        set(available_defect_kwargs.keys()),
        set(available_score_defects_kwargs.keys()),
    )


def test_template_context():
    available_template_kwargs = generate_template_kwargs()

    template = courier_wall.TemplateContext(
        '{{ NUMBER_ORDERS }}', available_template_kwargs,
    )
    assert template.render(**{'NUMBER_ORDERS': 0}) == '0'
    assert template.render(**{'NUMBER_ORDERS': 99}) == '99'

    with pytest.raises(courier_wall.CourierWallException):
        courier_wall.TemplateContext(
            '{{ incorrect_name }}', {'NUMBER_ORDERS', 'NUMBER_DEFECTIONS'},
        )
    with pytest.raises(courier_wall.CourierWallException):
        template.render()

    template_sum = courier_wall.TemplateContext(
        '{{ NUMBER_ORDERS + NUMBER_DEFECTIONS }}', available_template_kwargs,
    )
    assert template_sum.render(NUMBER_ORDERS=1, NUMBER_DEFECTIONS=2) == '3'

    template = courier_wall.TemplateContext(
        '{% if NUMBER_DEFECTIONS %}{{ NUMBER_DEFECTIONS }}{% endif %}',
        available_template_kwargs,
    )
    assert template.render(NUMBER_DEFECTIONS=0) == ''
    assert template.render(NUMBER_DEFECTIONS=99) == '99'


def test_template_kwargs():
    available_template_kwargs = generate_template_kwargs()
    available_defect_kwargs = courier_wall._generate_available_defect_kwargs(
        consts.EATS_COURIER_SCORING_DEFECT_TYPES,
    )
    available_score_defect_kwargs = (
        courier_wall._generate_available_score_defects_kwargs(
            consts.EATS_COURIER_SCORING_DEFECT_TYPES,
        )
    )

    for kwargs_name in available_template_kwargs:
        template = f'{{{{ {kwargs_name} }}}}'
        template_context = courier_wall.TemplateContext(
            template, available_template_kwargs,
        )
        template_kwargs = courier_wall._generate_template_kwargs(
            defect_kwargs=available_defect_kwargs,
            score_defect_kwargs=available_score_defect_kwargs,
            courier=COURIER,
        )
        assert template_context.render(**template_kwargs), kwargs_name


async def test_add_post(cron_context, mock_driver_wall_add):
    mock_driver_wall_add(
        check_request_drivers=[
            {
                'driver': '1_1',
                'title': 'title',
                'text': 'personal text: 1, 2, 1',
            },
        ],
    )
    await courier_wall.add_post(
        cron_context,
        request_id='request_id',
        title='title',
        text=(
            'personal text: {{NUMBER_ORDERS}}'
            ', {{NUMBER_DEFECTIONS}}, {{ NUMBER_DEFECTIONS_WITH_SCORE }}'
        ),
        teaser=None,
        url=None,
        url_open_mode='',
        image_id=None,
        couriers=[COURIER],
    )
