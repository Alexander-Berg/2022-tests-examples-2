import argparse
import re

from scripts.dev.create_stocktakers import main
from stall.model.user import User


# pylint: disable=too-many-locals,too-many-branches
async def test_create_stocktakers(tap, dataset):
    with tap.plan(12, 'проверяем скрипт создания счетчиков'):
        store1 = await dataset.store(lang='ru_RU')
        store2 = await dataset.store(lang='fr_FR')
        store3 = await dataset.store(lang='ru_RU')
        fake_stocktaker = await dataset.user(
            store_id=store3.store_id, fullname='не Счетчик 5', role='stocktaker'
        )
        fake_stocktaker.nick = None
        fake_stocktaker.company_id = None
        await fake_stocktaker.save()
        store_ids = store1.store_id + ' ' + \
                    store2.store_id + ' ' + store3.store_id

        args = argparse.Namespace(num_stocktakers=5,
                                  verbose=False,
                                  store_ids=store_ids,)
        tap.ok(await main(args), 'Счетчики созданы')

        users1 = await User.list(by='look', store_id=store1.store_id)
        users2 = await User.list(by='look', store_id=store2.store_id)
        users3 = await User.list(by='look', store_id=store3.store_id)

        patterns = {
            0: r'^(Счетчик |Schetchik_)\d$',
            1: r'^Stocktaker[ _]\d$',
            2: r'^(Счетчик|Stocktaker|Schetchik)[ _]\d$',
        }

        for i, users in enumerate([users1, users2, users3]):
            cnt = 0
            for u in users:
                if (re.match(patterns[i], u.fullname) and
                        re.match(patterns[i], u.nick)):
                    cnt += 1
            if i != 2:
                tap.eq_ok(cnt, 5, f'Найдено 5 юзеров для {i+1}-го склада')
            else:
                tap.eq_ok(cnt, 0, f'Найдено 0 юзеров для {i+1}-го склада')
                await fake_stocktaker.reload()
                tap.eq_ok(fake_stocktaker.nick, 'Schetchik_5', 'появился ник')
                tap.eq_ok(
                    fake_stocktaker.company_id,
                    store3.company_id,
                    'появилась компания'
                )

        for i, users in enumerate([users1, users2, users3]):
            ru_manager = None
            notru_manager = None
            for u in users:
                if u.fullname == 'Менеджер Инвентаризации':
                    ru_manager = u
                elif u.fullname == 'Manager Stocktaker':
                    notru_manager = u
            if i == 0:
                tap.ok(ru_manager, 'найден рус манагер в лавке1')
                tap.ok(not notru_manager, 'не найден нерус манагер в лавке1')
            elif i == 1:
                tap.ok(notru_manager, 'найден нерус манагер в лавке2')
                tap.ok(not ru_manager, 'не найден рус манагер в лавке2')
            elif i == 2:
                tap.ok(not notru_manager, 'не найден нерус манагер в лавке3')
                tap.ok(not ru_manager, 'не найден рус манагер в лавке3')
