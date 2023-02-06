from taxi_pyml.supportai.feature_extractors import base


def test_raw_extractor():
    raw_extractor = base.RawExtractor()
    assert raw_extractor(text='какой-то текст') == ('какой-то текст', str)


def test_constant_extractor():
    constant_extractor = base.ConstantExtractor(True)
    assert constant_extractor(
        text='номер моего заказа 12345678 я его оформил вчера',
    ) == (True, bool)
    assert constant_extractor('') == (True, bool)

    constant_extractor = base.ConstantExtractor('123')
    assert constant_extractor(
        text='номер моего заказа 12345678 я его оформил вчера',
    ) == ('123', str)


def test_number_extractor():
    number_extractor = base.NumberExtractor()
    assert number_extractor(
        text='номер моего заказа 12345678 я его оформил вчера',
    ) == (12345678, int)
    assert number_extractor(
        text='номер моего заказа 12345678 я его оформил вчера'
        '\nбыло где-то около 23 часов',
    ) == (None, None)
    assert number_extractor(text='я не помню номер моего заказа') == (
        None,
        None,
    )

    text = 'первые цифры моей карты 123456 на которую оформлена подписка'
    number_extractor = base.NumberExtractor(r'\d{6}')
    assert number_extractor(text=text) == (123456, int)
    assert number_extractor(text=f'{text} номер 12345') == (123456, int)
    assert number_extractor(text='подписка номер 12345') == (None, None)

    number_extractor = base.NumberExtractor(r'\d{3}.\d{2}')
    assert number_extractor(text='я заплатил 123.45 рублей') == (123.45, float)
    assert number_extractor(text='я заплатил 130 рублей') == (None, None)
    assert number_extractor(
        text='я заплатил 123.45 рублей\n хотя должен 100.23',
    ) == (None, None)


def test_date_extractor():
    date_extractor = base.DateExtractor()
    assert date_extractor(
        text='я оформил заказ 01-01-2021 где-то около 6 вечера',
    ) == ('01-01-2021', str)
    text = (
        'я оформил заказ 01-01-2021, а получил '
        'его только 06/01/2021, это разве нормально?'
    )
    assert date_extractor(text=text) == (None, None)

    date_extractor = base.DateExtractor(r'\d{4}/\d{2}/\d{2}')
    assert date_extractor(
        text='я оформил заказ 2021/01/01 где-то около 6 вечера',
    ) == ('2021/01/01', str)
    assert date_extractor(
        text='я оформил заказ 01-01-2021 где-то около 6 вечера',
    ) == (None, None)


def test_time_extractor():
    time_extractor = base.TimeExtractor()
    assert time_extractor(
        text='я оформил заказ в 18:05 сколько можно ждать?',
    ) == ('18:05', str)
    text = (
        'я оформил заказ 18:05, а получил '
        'его только в 20:21, это разве нормально?'
    )
    assert time_extractor(text=text) == (None, None)


def test_choice_from_variants_extractor():
    choice_from_variants_extractor = base.ChoiceFromVariantsExtractor(
        [
            {
                'regular_expression': 'appstore|app store|apple store',
                'value': 'App Store',
            },
            {
                'regular_expression': 'google play|googleplay|playmarket',
                'value': 'Google Play',
            },
            {
                'regular_expression': 'мобильный оператор|мтс|билайн|мегафон',
                'value': 'Мобильный оператор',
            },
        ],
    )
    assert choice_from_variants_extractor(
        text='я оформил подписку через appstore',
    ) == ('App Store', str)
    assert choice_from_variants_extractor(
        text='я оформил googleplay, но через кабинет у мтс',
    ) == (None, None)
    assert choice_from_variants_extractor(
        text='я очень мобильный человек',
    ) == (None, None)

    choice_from_variants_extractor = base.ChoiceFromVariantsExtractor(
        [
            {'regular_expression': 'Кнопка 1', 'value': 'App Store'},
            {'regular_expression': 'Кнопка 2', 'value': 'Google Play'},
            {'regular_expression': 'Кнопка 3', 'value': 'Мобильный оператор'},
        ],
        by_buttons=True,
    )
    assert choice_from_variants_extractor.get_buttons() == [
        'Кнопка 1',
        'Кнопка 2',
        'Кнопка 3',
    ]


def test_phone_number_extractor():
    phone_number_extractor = base.PhoneNumberExtractor()
    assert phone_number_extractor(text='89005553535') == (79005553535, int)
    assert phone_number_extractor(text='+7(900) 555-35-35') == (
        79005553535,
        int,
    )
    assert phone_number_extractor(
        text='Мой номер телефона 8.900.555.3535 !!!',
    ) == (79005553535, int)
    assert phone_number_extractor(
        text='Мой номер телефона +35 999 1234567 !!!',
    ) == (None, None)
