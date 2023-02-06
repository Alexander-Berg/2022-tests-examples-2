from collections import defaultdict
from stall.model.stash import Stash
from scripts.cron.sync_yt_order_reports import YtSyncReport


# pylint: disable=unused-argument, no-self-use
class YTClientMock:
    created_tables = []
    saved_stashes = defaultdict(lambda: defaultdict(list))

    def exists(self, *args, **kwargs):
        if args[0][1:] in self.created_tables:
            return True
        return False

    def create(self, *args, **kwargs):
        table = args[1][1:]
        if table == 'acceptance':
            self.created_tables.append(table)
            return
        raise Exception

    def mount_table(self, *args, **kwargs):
        return

    def insert_rows(self, *args, **kwargs):
        table = args[0][1:]
        for row in args[1]:
            self.saved_stashes[table][row['order_id']].append(row)


async def test_from_acceptance_report(tap, uuid):
    with tap.plan(9, 'Доверительная приемка'):
        stashes = []
        for i in range(2):
            report = [{
                        'product_id':   uuid(),
                        'count':        k,
                        'result_count': k,
                        'trash':        0,
                        'correction':   0,
                        'price':        k * 2
                    } for k in range(3)]
            report[1]['shelf_ids'] = [uuid()]
            report[2]['shelf_ids'] = [uuid()]
            report[2]['weight'] = 8
            stashes.append(
                await Stash.stash(
                    name=f'stash_{i}_{uuid()}',
                    group='order_report',
                    type='acceptance',
                    is_replicated=False,
                    user_id=uuid(),
                    order_id=uuid(),
                    report=report,
                    lsns=[uuid(), uuid()],
                    expired=60
                )
            )
        replicated_stash = await Stash.stash(
            name=f'stash_2_{uuid()}',
            group='order_report',
            type='acceptance',
            is_replicated=True,
            user_id=uuid(),
            order_id=uuid(),
            report=[],
            lsns=[uuid(), uuid()],
            expired=60
        )
        wrong_stash = await Stash.stash(
            name=f'stash_2_{uuid()}',
            group='order_report',
            type='wrong',
            is_replicated=False,
            user_id=uuid(),
            order_id=uuid(),
            report=[],
            lsns=[uuid(), uuid()],
            expired=60
        )

        yt_client = YTClientMock()
        sync_reports = YtSyncReport(yt_client, '')
        await sync_reports.sync_yt_order_reports()

        for stash in stashes:
            await stash.reload()
            tap.eq(
                stash.value['is_replicated'], True, 'stash.is_replicated')
            tap.eq_ok(
                len(yt_client.saved_stashes[
                    'acceptance'][stash.value['order_id']]),
                3, 'report replicated'
            )
            tap.eq_ok(
                yt_client.saved_stashes['acceptance'][stash.value[
                    'order_id']][2]['vars'].get('weight'),
                8, 'report replicated'
            )
        tap.not_in_ok(
            replicated_stash.value['order_id'],
            yt_client.saved_stashes['acceptance'],
            'report is not replicated twice'
        )
        tap.not_in_ok(
            wrong_stash.value['type'],
            yt_client.saved_stashes,
            'report is not replicated twice'
        )
        tap.eq_ok(
            yt_client.created_tables,
            ['acceptance'],
            'acceptance table is created'
        )
