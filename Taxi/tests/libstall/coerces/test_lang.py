from libstall.model.coerces import coerce_lang


async def test_lang(tap):
    with tap.plan(3, 'Код языка должен быть четырехбуквенным'):
        with tap.raises(ValueError):
            coerce_lang('ru')
        with tap.raises(ValueError):
            coerce_lang('RU_ru')
        tap.eq(coerce_lang('ru_RU'), 'ru_RU', 'Успех')
