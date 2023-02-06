import pytest

from stall.model import schet_handler


async def test_schets_handler(tap):
    calls = []

    def callback(kwargs):
        calls.append(kwargs)

    with tap.plan(6, 'запуск хэндлера'):
        handler = schet_handler.SchetHandler('test_callback_cron')
        tap.ok(handler.imported, 'handler imported')

        tap.eq(len(calls), 0, 'none calls proceeded')

        await handler.handle(callback=callback)
        tap.eq(len(calls), 1, 'first call proceeded')
        tap.eq(calls[-1], {}, 'first call with empty kwargs')

        await handler.handle(callback=callback, company_id='123')
        tap.eq(len(calls), 2, 'second call proceeded')
        tap.eq(calls[-1], {'company_id': '123'}, 'second call with company_id')


async def test_schets_handler_list(tap):
    with tap.plan(1, 'список хэндлеров'):
        all_crons = schet_handler.SchetHandler.list()
        tap.eq(all_crons, [
            schet_handler.SchetHandler('dummy_cron'),
            schet_handler.SchetHandler('test_callback_cron'),
        ], 'list all crons ordered by name')


@pytest.fixture(autouse=True)
def crons_config_mock(monkeypatch):
    # pylint: disable=protected-access
    monkeypatch.setattr(
        schet_handler, 'SCHETS',
        schet_handler._load_schets('tests/model/schet_handler/schets.yaml')
    )
