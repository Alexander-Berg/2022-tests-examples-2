import pytest

from stall.model.lock import ProlongLock
from stall.model.order_log import OrderLog


async def test_done(tap, dataset):
    with tap.plan(10, 'завершение саджеста'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'waiting', 'сабстатус')

        suggest = await dataset.suggest(order, status='request')
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.status, 'request', 'статус')
        tap.eq(suggest.revision, 1, 'revision')

        tap.ok(await suggest.done(), 'саджест завершён')

        tap.eq(suggest.status, 'done', 'статус')
        tap.eq(suggest.revision, 2, 'revision')

        with tap.subtest(None, 'Получение логов') as taps:
            cursor = None
            while True:
                logs = await OrderLog.list_by_order(order,
                                                    limit=3,
                                                    cursor_str=cursor)
                taps.ok(logs, f'Порция логов получена len={len(logs.list)}')
                for l in logs:
                    taps.eq(l.status, 'processing', f'статус {l.status}')
                    taps.in_ok(
                        l.source,
                        ('suggest_done', 'save'),
                        f'source {l.source}'
                    )
                    taps.eq(l.order_id,
                            order.order_id,
                            f'order_id {l.order_id}')

                cursor = logs.cursor_str
                if cursor is None:
                    break


async def test_error(tap, dataset):
    with tap.plan(9, 'завершение саджеста с ошибкой'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'waiting', 'сабстатус')

        suggest = await dataset.suggest(order, status='request')
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.status, 'request', 'статус')

        tap.ok(await suggest.done(status='error',
                                  reason={
                                      'code': 'PRODUCT_ABSENT',
                                      'count': 27
                                  }),
               'саджест завершён')

        tap.eq(suggest.status, 'error', 'статус')
        tap.eq(suggest.reason,
               {'code': 'PRODUCT_ABSENT', 'count': 27},
               'reason')

        with tap.subtest(None, 'Получение логов') as taps:
            cursor = None
            while True:
                logs = await OrderLog.list_by_order(order,
                                                    limit=3,
                                                    cursor_str=cursor)
                taps.ok(logs, f'Порция логов получена len={len(logs.list)}')
                for l in logs:
                    taps.eq(l.status, 'processing', f'статус {l.status}')
                    taps.in_ok(
                        l.source,
                        ('suggest_error', 'save'),
                        f'source {l.source}'
                    )
                    taps.eq(l.order_id,
                            order.order_id,
                            f'order_id {l.order_id}')

                cursor = logs.cursor_str
                if cursor is None:
                    break


async def test_lock_error(tap, dataset):
    with tap.plan(7, 'заблокирован ордер'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'waiting', 'сабстатус')

        suggest = await dataset.suggest(order, status='request')
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.status, 'request', 'статус')

        async with ProlongLock(order.order_id,
                               rm=True,
                               timeout=3600,
                               after_success_timeout=0) as lock:
            tap.ok(lock, 'Блокировка взята')
            with tap.raises(ProlongLock.TimeoutError, 'Не взять блокировку'):
                await suggest.done(status='error',
                                   reason={
                                       'code': 'PRODUCT_ABSENT',
                                       'count': 27
                                   },
                                   lock_timeout=.1)


async def test_user_error(tap, dataset):
    with tap.plan(8, 'не  тот юзер'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'waiting', 'сабстатус')

        suggest = await dataset.suggest(order, status='request')
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.status, 'request', 'статус')

        user = await dataset.user()
        tap.ok(user, 'пользователь сгенерирован')
        tap.ok(user.store_id, 'склад у него есть')

        with tap.raises(suggest.ErOrderWrongUser, 'Не тот пользователь'):
            await suggest.done(status='error',
                               reason={
                                   'code': 'PRODUCT_ABSENT',
                                   'count': 27
                               },
                               user=user)


async def test_user_not_processing(tap, dataset):
    with tap.plan(8, 'не  тот юзер'):
        user = await dataset.user()
        tap.ok(user, 'пользователь сгенерирован')
        tap.ok(user.store_id, 'склад есть')

        order = await dataset.order(status='complete',
                                    estatus='waiting',
                                    store_id=user.store_id,
                                    users=[user.user_id])
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.status, 'complete', 'статус')
        tap.eq(order.estatus, 'waiting', 'сабстатус')

        suggest = await dataset.suggest(order, status='request')
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.status, 'request', 'статус')

        with tap.raises(suggest.ErOrderIsNotProcessing, 'Не процессинг'):
            await suggest.done(status='error',
                               reason={
                                   'code': 'PRODUCT_ABSENT',
                                   'count': 27
                               },
                               user=user)


async def test_user_not_waiting(tap, dataset):
    with tap.plan(8, 'не  тот юзер'):
        user = await dataset.user()
        tap.ok(user, 'пользователь сгенерирован')
        tap.ok(user.store_id, 'склад есть')

        order = await dataset.order(status='processing',
                                    estatus='done',
                                    store_id=user.store_id,
                                    users=[user.user_id])
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'done', 'сабстатус')

        suggest = await dataset.suggest(order, status='request')
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.status, 'request', 'статус')

        with tap.raises(suggest.ErOrderIsNotWait, 'Не процессинг'):
            await suggest.done(status='error',
                               reason={
                                   'code': 'PRODUCT_ABSENT',
                                   'count': 27
                               },
                               user=user)


@pytest.mark.parametrize('status', ['done', 'error'])
async def test_no_request_pass(tap, dataset, status):
    with tap.plan(7, 'завершение не в статусе request'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'waiting', 'сабстатус')

        suggest = await dataset.suggest(order, status=status)
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.status, status, 'статус')

        tap.ok(await suggest.done(status=status), 'саджест завершён')

        tap.eq(suggest.status, status, 'статус')


async def test_change_done(tap, dataset):
    with tap.plan(22, 'Исправление саджеста done-done'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'waiting', 'сабстатус')

        suggest = await dataset.suggest(order,
                                        status='request',
                                        conditions={
                                            'editable': True,
                                            'all': True
                                        })
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.status, 'request', 'статус')
        tap.eq(suggest.revision, 1, 'revision')

        tap.ok(await suggest.done(), 'саджест завершён')

        tap.eq(suggest.status, 'done', 'статус')
        tap.eq(suggest.revision, 2, 'revision')
        tap.eq(suggest.result_valid, suggest.valid, 'результирующий СХ')
        tap.eq(suggest.result_count, suggest.count, 'результирующее число')

        prev_count = suggest.count
        prev_valid = suggest.valid
        tap.ok(prev_valid, 'Предыдущее значение СГ заполнено')
        tap.ok(prev_count, 'Предыдущее количество > 0')
        tap.ok(await suggest.done('done',
                                  count=prev_count - 1,
                                  valid='2017-12-15',
                                  reason={
                                      'code': 'CHANGE_COUNT',
                                  }),
               'Исправили количество в done')

        tap.eq(suggest.result_count, prev_count - 1, 'итого записалось')
        tap.eq(suggest.result_valid, suggest.valid, 'Значение СГ игнорировано')

        tap.ok(await suggest.done('done',
                                  count=prev_count + 1,
                                  valid='2017-12-15',
                                  reason={
                                      'code': 'CHANGE_VALID',
                                  }),
               'Исправили СГ в done')
        tap.eq(suggest.result_count, prev_count - 1, 'итого не менялось')
        tap.eq(suggest.result_valid.strftime('%F'),
               '2017-12-15',
               'Значение срока годности поменялось')

        tap.ok(await suggest.done('done',
                                  count=prev_count + 7,
                                  valid='2017-12-11',
                                  reason={
                                      'code': 'CHANGE_COUNT_VALID',
                                  }),
               'Исправили СГ и количество в done')
        tap.eq(suggest.result_count, prev_count + 7, 'итого записалось')
        tap.eq(suggest.result_valid.strftime('%F'),
               '2017-12-11',
               'Значение срока годности поменялось')


async def test_change_done_noeditable(tap, dataset):
    with tap.plan(3, 'Выброс исключения без editable'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        suggest = await dataset.suggest(order,
                                        status='done',
                                        conditions={'all': True})
        tap.eq(suggest.status, 'done', 'саджест создан сразу done')

        with tap.raises(suggest.ErSuggestIsNotEditable,
                        'Нельзя редактировать'):
            await suggest.done('done',
                               count=22,
                               valid='2017-12-15',
                               reason={
                                   'code': 'CHANGE_COUNT',
                               })


async def test_error_denied(tap, dataset):
    with tap.plan(6, 'завершение саджеста с ошибкой запрещено'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'waiting', 'сабстатус')

        suggest = await dataset.suggest(
            order,
            status='request',
            conditions={'error': False}
        )
        tap.ok(suggest, 'саджест сгенерирован')
        tap.eq(suggest.status, 'request', 'статус')

        with tap.raises(
                suggest.ErSuggestErrorDenided,
                'Нельзя закрывать в error',
        ):
            await suggest.done(
                status='error',
                reason={
                    'code': 'PRODUCT_ABSENT',
                    'count': 27
                },
            )


async def test_change_max_count(tap, dataset):
    with tap.plan(3, 'Выброс исключения без editable'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        suggest = await dataset.suggest(order,
                                        status='done',
                                        conditions={
                                            'all': True,
                                            'max_count': True
                                        })
        tap.eq(suggest.status, 'done', 'саджест создан сразу done')

        with tap.raises(suggest.ErSuggestCount,
                        'Нельзя вводить больше число чем можно'):
            await suggest.done('done', count=suggest.count + 1)


async def test_need_valid(tap, dataset):
    with tap.plan(5, 'Выброс исключения без editable'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        suggest = await dataset.suggest(order,
                                        status='request',
                                        valid=None,
                                        conditions={
                                            'all': True,
                                            'need_valid': True,
                                        })
        tap.eq(suggest.valid, None, 'valid не проставлен')
        tap.eq(suggest.status, 'request', 'status')

        with tap.raises(suggest.ErSuggestValidRequired,
                        'Бросает исключение без valid'):
            await suggest.done('done', count=suggest.count)

        tap.ok(await suggest.done('done', count=0), 'с нулём закрывается')


async def test_logs(tap, dataset):
    with tap.plan(16, 'Смотрим логи'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        suggest = await dataset.suggest(order,
                                        count=1,
                                        conditions={
                                            'cancelable': True,
                                        })
        tap.eq(suggest.status, 'request', 'status')
        tap.ok(await suggest.done('done', count=1), 'закрыли 1')

        await suggest.reload()
        tap.eq(len(suggest.vars['logs']), 1, 'логов 1')
        tap.eq(suggest.vars['logs'][0]['result_count'], None,
               'result_count')
        tap.eq(suggest.vars['logs'][0]['status'], 'request',
               'status')

        tap.ok(await suggest.done(status='cancel'), 'отменили')

        await suggest.reload()
        tap.eq(len(suggest.vars['logs']), 2, 'логов 2')
        tap.eq(suggest.vars['logs'][1]['result_count'], 1,
               'result_count 1 ')
        tap.eq(suggest.vars['logs'][1]['status'], 'done',
               'status done')
        tap.eq(suggest.vars['logs'][1]['required_status'], 'cancel',
               'required_status')

        tap.ok(await suggest.done(count=1), 'заново закрыли на 1')

        await suggest.reload()
        tap.eq(len(suggest.vars['logs']), 3, 'логов 3')
        tap.eq(suggest.vars['logs'][2]['result_count'], None,
               'сохранили старый result_count')
        tap.eq(suggest.vars['logs'][2]['status'], 'request',
               'status done')
        tap.eq(suggest.vars['logs'][2]['required_status'], 'done',
               'status done' )


async def test_check_more_no_stocks(tap, dataset):
    with tap.plan(1, 'Закрытие саджеста check_more на продукт без остатка'):
        store = await dataset.store(options={'exp_condition_zero': False})
        user = await dataset.user(role='executer', store=store)
        order = await dataset.order(
            store=store,
            users=[user.user_id],
            status='processing',
            estatus='waiting',
            type='check_more'
        )
        shelf = await dataset.shelf(store=store)
        suggest = await dataset.suggest(order, type='check_more', shelf=shelf)
        product = await dataset.product()

        with tap.raises(suggest.ErSuggestWrongProductId):
            await suggest.done(product_id=product.product_id, count=35)


async def test_done_product_no_stocks_exp(tap, dataset):
    with tap.plan(3, 'Cаджеста check_more на продукт без остатка эксп'):
        store = await dataset.store(options={'exp_condition_zero': True})
        user = await dataset.user(role='executer', store=store)
        order = await dataset.order(
            store=store,
            users=[user.user_id],
            status='processing',
            estatus='waiting',
            type='check_more'
        )
        shelf = await dataset.shelf(store=store)
        suggest = await dataset.suggest(order, type='check_more', shelf=shelf)
        product = await dataset.product()

        tap.ok(
            await suggest.done(product_id=product.product_id, count=35),
            'Закрыли саджест успешно'
        )

        await suggest.reload()
        tap.eq(suggest.product_id, product.product_id, 'Продукт')
        tap.eq(suggest.result_count, 35, 'Кол-во продуктов')


async def test_done_check_more(tap, dataset):
    with tap.plan(3, 'check_more с остатком на продукт'):
        store = await dataset.store()
        user = await dataset.user(role='executer', store=store)
        order = await dataset.order(
            store=store,
            users=[user.user_id],
            status='processing',
            estatus='waiting',
            type='check_more'
        )
        shelf = await dataset.shelf(store=store)
        suggest = await dataset.suggest(order, type='check_more', shelf=shelf)
        product = await dataset.product()
        stock = await dataset.stock(store=store, product=product, count=0)

        tap.ok(
            await suggest.done(product_id=stock.product_id, count=35),
            'Закрыли саджест успешно'
        )

        await suggest.reload()
        tap.eq(suggest.product_id, product.product_id, 'Продукт')
        tap.eq(suggest.result_count, 35, 'Кол-во продуктов')


@pytest.mark.parametrize('order_type', [
    'check_product_on_shelf',
    'inventory_check_more',
])
async def test_done_product_no_stocks_inv(tap, dataset, order_type):
    with tap.plan(1, 'check_more без остатка но тип документа позволяет'):
        store = await dataset.store()
        user = await dataset.user(role='executer', store=store)
        order = await dataset.order(
            store=store,
            users=[user.user_id],
            status='processing',
            estatus='waiting',
            type=order_type,
        )
        shelf = await dataset.shelf(store=store)
        suggest = await dataset.suggest(order, type='check_more', shelf=shelf)
        product = await dataset.product()

        tap.ok(
            await suggest.done(product_id=product.product_id, count=35),
            'Закрыли саджест успешно'
        )
