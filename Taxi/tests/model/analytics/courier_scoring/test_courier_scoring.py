from stall.model.analytics.courier_scoring import CourierScoring


async def test_model_save_list(tap, now, uuid):
    with tap.plan(4, 'сохранение батча скорингов'):
        some_date = now().date()
        external_courier_id = uuid()
        region_name = uuid()

        scoring = await CourierScoring(
            statistics_week=some_date,
            external_courier_id=external_courier_id,
            shift_delivery_type='foot',
            region_name=region_name,
            rating_position=10,
        ).save()

        loaded_scoring = await CourierScoring.load(scoring.courier_scoring_id)
        tap.ok(loaded_scoring, 'Скоринг был сохранен и загружен')
        tap.eq_ok(loaded_scoring.rating_position, scoring.rating_position,
                  'Позиция в рейтинге верная')

        rewrite_scoring = CourierScoring(
            statistics_week=some_date,
            external_courier_id=external_courier_id,
            shift_delivery_type='foot',
            region_name=region_name,
            rating_position=2,
        )
        await CourierScoring.save_list('chunks', items=[rewrite_scoring])

        scoring2 = await CourierScoring.load(scoring.courier_scoring_id)
        tap.ok(scoring2, 'Скоринг пересохранен с тем же id')
        tap.eq_ok(scoring2.rating_position, rewrite_scoring.rating_position,
                  'Скоринг изменился на новый')
