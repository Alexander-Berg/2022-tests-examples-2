import pytest

from eats_order_integration.components.engines import yandex_eda
from eats_order_integration.internal import exceptions


@pytest.fixture(autouse=True)
def _integration_engines_config(client_experiments3):
    client_experiments3.add_record(
        consumer='eats_order_integration/integration_engines_config',
        config_name='eats_order_integration_integration_engines_config',
        args=[{'name': 'engine_name', 'type': 'string', 'value': 'test1'}],
        value={'engine_name': 'test1', 'engine_class_name': 'YandexEdaEngine'},
    )


@pytest.mark.parametrize(
    'engine_id,expected_engine_type', [[1, yandex_eda.YandexEdaEngine]],
)
async def test_should_return_engine(
        engine_id, expected_engine_type: type, web_context,
):
    engine = await web_context.engine_selector.select_engine(engine_id)
    assert isinstance(engine, expected_engine_type)


@pytest.mark.parametrize('engine_id', [2, 3])
async def test_should_raise_exception(engine_id, web_context):
    with pytest.raises(exceptions.CannotFindIntegrationEngine):
        await web_context.engine_selector.select_engine(engine_id)


async def test_should_return_singleton(web_context):
    engine1 = await web_context.engine_selector.select_engine(1)
    engine2 = await web_context.engine_selector.select_engine(1)

    assert isinstance(engine1, yandex_eda.YandexEdaEngine)
    assert isinstance(engine2, yandex_eda.YandexEdaEngine)

    assert id(engine1) == id(engine2)
