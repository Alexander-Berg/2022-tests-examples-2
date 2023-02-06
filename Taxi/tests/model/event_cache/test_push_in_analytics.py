from stall.model.event_cache import EventQueue
from stall.model.analytics.event_cache import EventCache as EventCacheAnalytics


class SomeClass:
    @staticmethod
    def method_in_class(**kwargs):
        return kwargs

async def test_full_cycle(tap, dataset, push_events_cache, job):
    with tap.plan(3, 'Сложим ивент и пушнем его'):
        store_problem = await dataset.store_problem()
        await store_problem.save(
            events=[EventQueue.create(
                tube='job',
                caller=None,
                callback=SomeClass.method_in_class
            )]
        )

        cursor = await EventCacheAnalytics.list(
            by='full',
            db={'shard': store_problem.shardno},
            conditions=(
                ('tbl', 'store_problems'),
                ('pk', store_problem.store_problem_id),
                ('type', 'queue'),
            )
        )

        tap.eq(len(cursor.list), 1, 'События сохранились в бд')
        tap.note('Пушнули ивент в sqs')
        await push_events_cache(
            store_problem,
            event_type='queue',
            database='analytics',
        )
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        cursor = await EventCacheAnalytics.list(
            by='full',
            db={'shard': store_problem.shardno},
            conditions=(
                ('tbl', 'store_problems'),
                ('pk', store_problem.store_problem_id),
                ('type', 'queue'),
            )
        )

        tap.eq(len(cursor.list), 0, 'Событие удалено из бд')
