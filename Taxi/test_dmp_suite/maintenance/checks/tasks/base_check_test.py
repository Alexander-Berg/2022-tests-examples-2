import pytest

from dmp_suite.maintenance.checks.tasks import PropertyCheck, AggregateCheck, aggregate_desc_fn
from dmp_suite.yt.task.etl.external_transform import external_source


def test_raises_incompatible():
    with pytest.raises(ValueError):
        AggregateCheck(
            name="DummyCheckTestRaises",
            error_source=external_source([]),
            carry_history=False,
            description_fn=aggregate_desc_fn(''),
        ).reporters(
            star_trek='some_st',
        )

    # бросает исключение из-за дефолтного значение
    # параметра `star_trek` в методе `reporters`.
    with pytest.raises(ValueError):
        PropertyCheck(
            name="DummyCheckTestRaises",
            error_source=external_source([]),
            error_msg="i am error.",
            carry_history=False,
        ).reporters(
            juggler='experimental',
        )
