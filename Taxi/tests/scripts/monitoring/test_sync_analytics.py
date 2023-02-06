import datetime
from stall.model.stash import Stash
from stall.monitoring import sync_analytics

class ReporterStub:
    # pylint: disable=unused-argument

    def __init__(self):
        self.data = {}

    async def send_value(self, sensor_name, value, agg=None):
        self.data[sensor_name] = value

async def test_sync_analytic(tap, now):
    tap.plan(3)
    try:
        await Stash.unstash(name='sync_analytics_gp_processed')
    except AttributeError:
        pass

    with tap.subtest(1, 'Процесс синхронизации окончен') as taps:
        processed_stash = await Stash(
            name='sync_analytics_gp_processed',
            expired=None,
            value={
                'date_in_process': None
            }
        ).save()

        reporter = ReporterStub()
        await sync_analytics.handle(reporter)

        taps.eq_ok(
            reporter.data['sync_analytics_not_processed'],
            0,
            'Все данные синхронизированы'
        )

    with tap.subtest(1, 'Идёт синхронизация последней даты') as taps:
        today = now().date()
        processed_stash.value['date_in_process'] = today
        processed_stash.value['max_date'] = today
        await processed_stash.save()

        reporter = ReporterStub()
        await sync_analytics.handle(reporter)

        taps.eq_ok(
            reporter.data['sync_analytics_not_processed'],
            1,
            'Осталась 1 дата.'
        )

    with tap.subtest(1, 'Начало процесса синхронизации') as taps:
        today = now().date()
        processed_stash.value['date_in_process'] = (
            today - datetime.timedelta(days=7)
        )
        processed_stash.value['max_date'] = today
        await processed_stash.save()

        reporter = ReporterStub()
        await sync_analytics.handle(reporter)

        taps.eq_ok(
            reporter.data['sync_analytics_not_processed'],
            8,
            'Необходимо синхронизировать данные за 8 дней '
            'Т.к. включительно'
        )


