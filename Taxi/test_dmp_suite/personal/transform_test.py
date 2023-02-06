from unittest import mock
from dmp_suite.personal.transform import replace_phone_ids
from contextlib import contextmanager


@contextmanager
def mocked_phones(resulting_dict):
    with mock.patch('dmp_suite.personal.transform.Personal') as Personal:
        Personal.return_value.phones.get_values.return_value = resulting_dict
        yield


def test_phone_replacer_automatic_field_name():
    # Если передана только исходная колонка с id,
    # то результат будет помещён в такую же, но без суффикса
    # _id.
    replacer = replace_phone_ids('phone_id')

    with mocked_phones({'100500': 'real value'}):
        result = replacer([{'name': 'Vasya', 'phone_id': '100500'}])

    assert result == [{'name': 'Vasya', 'phone': 'real value'}]


def test_phone_replacer_with_manual_field_name():
    # Но имя колонки можно задать вручную:
    replacer = replace_phone_ids('phone_id', 'telephone')

    with mocked_phones({'100500': 'real value'}):
        result = replacer([{'name': 'Vasya', 'phone_id': '100500'}])

    assert result == [{'name': 'Vasya', 'telephone': 'real value'}]


def test_phone_replacer_can_keep_original_column():
    # Чтобы не удалять оригинальную колонку, можно задать
    # атрибут keep_id_column:
    replacer = replace_phone_ids('phone_id', keep_id_column=True)

    with mocked_phones({'100500': 'real value'}):
        result = replacer([{'name': 'Vasya', 'phone_id': '100500'}])

    assert result == [{'name': 'Vasya',
                       'phone_id': '100500',
                       'phone': 'real value'}]


def test_phone_replacer_returns_none_if_no_data_in_pd():
    # Если в сервисе ПД нет каких то данных, то вместо них в колонку
    # придёт None.
    # Для наглядности теста тут оставляем оригинальную коллонку:
    replacer = replace_phone_ids('phone_id', keep_id_column=True)

    # В симуляции ответа, результат есть только для номера 100500,
    # но не для 42
    with mocked_phones({'100500': 'real value'}):
        result = replacer([
            {'name': 'Vasya', 'phone_id': '100500'},
            {'name': 'Mary',  'phone_id': '42'},
        ])

    assert result == [
        {'name': 'Vasya', 'phone_id': '100500', 'phone': 'real value'},
        {'name': 'Mary',  'phone_id': '42',     'phone': None},
    ]
