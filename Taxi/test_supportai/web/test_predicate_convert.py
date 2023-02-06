import pytest

from supportai.generated.service.swagger.models import api as api_models
from supportai.utils import predicate_helpers


@pytest.mark.parametrize(
    ('code_predicate', 'is_form_result'),
    [
        ('order_id = 12345', True),
        ('order_id = 12345 and status > 200', True),
        ('order_id = 12345 or status > 200', False),
        ('status > 200 and not text contains "qwerty"', True),
        ('not a > 4', False),
    ],
)
async def test_predicate_convert_to_form(code_predicate, is_form_result):
    filled_predicate = predicate_helpers.fill_predicate(
        api_models.Predicate(
            predicates=[
                api_models.PredicateItem(
                    is_active=True, type='code', code_predicate=code_predicate,
                ),
            ],
        ),
    )
    if is_form_result:
        assert filled_predicate.predicates[0].form_predicate
    else:
        assert not filled_predicate.predicates[0].form_predicate


@pytest.mark.parametrize(
    'form_predicate',
    [
        [('order_id', '=', '12345')],
        [('order_id', '=', '12345'), ('status', '>', '2')],
        [('order_id', 'contains', ['123', '45'])],
        pytest.param(
            [('order_id', 'qwerty', '12345')],
            marks=pytest.mark.xfail(
                raises=predicate_helpers.PredicateException, strict=True,
            ),
        ),
        pytest.param(
            [('order_id', '=', ['123', '45'])],
            marks=pytest.mark.xfail(
                raises=predicate_helpers.PredicateException, strict=True,
            ),
        ),
    ],
)
async def test_predicate_convert_to_code(form_predicate):
    filled_predicate = predicate_helpers.fill_predicate(
        api_models.Predicate(
            predicates=[
                api_models.PredicateItem(
                    is_active=True,
                    type='form',
                    form_predicate=[
                        api_models.FormPredicateItem(
                            feature=item[0], operator=item[1], value=item[2],
                        )
                        for item in form_predicate
                    ],
                ),
            ],
        ),
    )
    assert filled_predicate.predicates[0].code_predicate
