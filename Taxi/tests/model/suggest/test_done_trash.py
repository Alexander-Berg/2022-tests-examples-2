import pytest



@pytest.mark.parametrize('reason_code', [
    (None, 'TRASH_DAMAGE'),
    ('TRASH_DAMAGE', 'TRASH_DAMAGE'),
    ('TRASH_TTL', 'TRASH_TTL'),
    ('TRASH_DECAYED', 'TRASH_DECAYED'),
    ('TRASH_ORDINANCE', 'TRASH_ORDINANCE'),
    ('TRASH_MOL', 'TRASH_MOL'),
    ('TRASH_ACCIDENT', 'TRASH_ACCIDENT'),
])
async def test_done(tap, dataset, reason_code):
    with tap.plan(8, 'Работа conditions trash_reason'):
        order = await dataset.order(status='processing', estatus='waiting')
        tap.ok(order, 'ордер сгенерирован')
        suggest = await dataset.suggest(order,
                                        status='request',
                                        valid=None,
                                        conditions={
                                            'trash_reason': True,
                                            'editable': True,
                                            'all': True,
                                        })

        with tap.raises(suggest.ErSuggestReasonRequired,
                        'Бросает исключение без valid'):
            await suggest.done('done',
                               count=suggest.count,
                               reason={'code': 'CHANGE_COUNT'})



        tap.ok(
            await suggest.done(reason={'code': reason_code[0]}),
            f'Закрыли саджест с кодом {reason_code[0]}'
        )
        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq(suggest.reason.code, reason_code[1], 'код сохранился')


        tap.ok(
            await suggest.done(reason={'code': 'CHANGE_COUNT'}, count=1),
            'Отредактировали саджест'
        )
        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq(suggest.reason.code, reason_code[1], 'код сохранился')
