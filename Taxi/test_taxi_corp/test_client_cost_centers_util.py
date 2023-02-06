import io

import xlwt

MSG_ID = 'id полей не должны повторяться: hidden_field_uuid_id, ride_purpose'
MSG_TITLE = 'названия не должны повторяться: Кастомное поле, Цель поездки'


ERRORS = {
    'default_exists': {
        'code': 'CLIENT_DUPLICATE_DEFAULT_COST_CENTERS',
        'message': 'client already has default cost center options',
    },
    'cost_centers_not_found': {
        'code': 'CLIENT_COST_CENTERS_NOT_FOUND',
        'message': 'client does not have such cost_centers_id',
    },
    'cannot_delete_cost_center_with_users': {
        'code': 'COST_CENTERS_CANNOT_DELETE_WITH_USERS',
        'message': 'cannot delete cost center with users on it',
    },
    'cannot_move_users_to_same_id': {
        'code': 'COST_CENTERS_CANNOT_MOVE_USERS_TO_SAME_ID',
        'message': 'cannot move users to the same id',
    },
    'cannot_delete_default_cost_center': {
        'code': 'COST_CENTERS_CANNOT_DELETE_DEFAULT',
        'message': 'cannot delete default cost center',
    },
    'default_must_exist': {
        'code': 'CLIENT_DEFAULT_COST_CENTERS_MUST_EXIST',
        'message': (
            'client should have at least one default, cannot make it '
            'not default'
        ),
    },
    'default_less_fields': {
        'code': 'COST_CENTERS_DIFFERENT_FIELDS',
        'message': 'нельзя удалять поля в основном наборе (можно скрыть их)',
    },
    'default_no_reorder': {
        'code': 'COST_CENTERS_DIFFERENT_FIELDS',
        'message': 'нельзя менять местами поля в основном наборе',
    },
    'different_fields_count': {
        'code': 'COST_CENTERS_DIFFERENT_FIELDS',
        'message': 'разное число полей в дополнительном и основном наборе',
    },
    'different_fields_id': {
        'code': 'COST_CENTERS_DIFFERENT_FIELDS',
        'message': 'разные id полей в дополнительном и основном наборе',
    },
    'different_fields_title': {
        'code': 'COST_CENTERS_DIFFERENT_FIELDS',
        'message': 'разные имена полей в дополнительном и основном наборе',
    },
    'different_fields_services': {
        'code': 'COST_CENTERS_DIFFERENT_FIELDS',
        'message': 'разные сервисы в дополнительном и основном наборе',
    },
    'duplicate_ids': {
        'code': 'COST_CENTERS_DUPLICATE_FIELD_IDS',
        'message': MSG_ID,
    },
    'duplicate_titles': {
        'code': 'COST_CENTERS_DUPLICATE_FIELD_TITLES',
        'message': MSG_TITLE,
    },
    'empty_title': {
        'code': 'COST_CENTERS_EMPTY_TITLES',
        'message': 'заголовок у поля #2 не должен быть пустым',
    },
    'empty_value': {
        'code': 'COST_CENTERS_EMPTY_VALUES',
        'message': (
            'значения для выбора у поля "Цель поездки" '
            'не должны быть пустыми'
        ),
    },
    'same_name': {
        'code': 'CLIENT_DUPLICATE_COST_CENTERS_NAMES',
        'message': 'центр затрат с таким названием уже существует',
    },
    'too_many_options': {
        'code': 'COST_CENTERS_TOO_MANY_OPTIONS',
        'message': 'максимальное число центров затрат: 2',
    },
    'too_many_fields': {
        'code': 'COST_CENTERS_TOO_MANY_FIELDS',
        'message': 'максимальное число полей: 2, получено: 4',
    },
    'too_few_fields': {
        'code': 'COST_CENTERS_TOO_FEW_FIELDS',
        'message': 'минимальное число полей: 5, получено: 3',
    },
    'too_many_active_fields': {
        'code': 'COST_CENTERS_TOO_MANY_ACTIVE_FIELDS',
        'message': 'максимальное число активных полей: 2, получено: 3',
    },
    'too_few_active_fields': {
        'code': 'COST_CENTERS_TOO_FEW_ACTIVE_FIELDS',
        'message': 'минимальное число активных полей: 4, получено: 3',
    },
    'too_long_field_title': {
        'code': 'COST_CENTERS_TOO_LONG_FIELD_TITLE',
        'message': 'максимальная длина заголовка поля: 10, получено: 12',
    },
    'too_short_field_title': {
        'code': 'COST_CENTERS_TOO_SHORT_FIELD_TITLE',
        'message': 'минимальная длина заголовка поля: 15, получено: 12',
    },
    'too_long_value': {
        'code': 'COST_CENTERS_TOO_LONG_VALUE',
        'message': (
            'максимальная длина значения для поля "Центр затрат"'
            ' — 2, а у вас {}'
        ),
    },
    'too_many_field_values': {
        'code': 'COST_CENTERS_TOO_MANY_FIELD_VALUES',
        'message': (
            'максимальное число значений для поля Другое поле: 2, получено: 3'
        ),
    },
    'too_few_field_values': {
        'code': 'COST_CENTERS_TOO_FEW_FIELD_VALUES',
        'message': (
            'минимальное число значений для поля Центр затрат: 4, получено: 2'
        ),
    },
    'creation_not_allowed': {
        'code': 'COST_CENTERS_CREATION_NOT_ALLOWED',
        'message': 'для вашего аккаунта пока не разрешено создание новых ЦЗ',
    },
}

CORP_TRANSLATIONS = {
    'error.cost_center.duplicate_names': {
        'ru': 'центр затрат с таким названием уже существует',
    },
    'error.cost_center.duplicate_field_values': {
        'ru': 'недопустимы повторяющиеся значения {} у полей: {}',
    },
    'error.cost_center.duplicate_field_titles': {
        'ru': 'названия не должны повторяться: {}',
    },
    'error.cost_center.duplicate_field_ids': {
        'ru': 'id полей не должны повторяться: {}',
    },
    'error.cost_center.empty_titles': {
        'ru': 'заголовок у поля #{} не должен быть пустым',
    },
    'error.cost_center.empty_values': {
        'ru': 'значения для выбора у поля "{}" не должны быть пустыми',
    },
    'error.cost_center.cant_remove_fields_from_default': {
        'ru': 'нельзя удалять поля в основном наборе (можно скрыть их)',
    },
    'error.cost_center.cant_reorder_fields_in_default': {
        'ru': 'нельзя менять местами поля в основном наборе',
    },
    'error.cost_center.different_fields_count': {
        'ru': 'разное число полей в дополнительном и основном наборе',
    },
    'error.cost_center.different_fields_title': {
        'ru': 'разные имена полей в дополнительном и основном наборе',
    },
    'error.cost_center.different_fields_services': {
        'ru': 'разные сервисы в дополнительном и основном наборе',
    },
    'error.cost_center.different_fields_id': {
        'ru': 'разные id полей в дополнительном и основном наборе',
    },
    'error.cost_center.too_many_options': {
        'ru': 'максимальное число центров затрат: {}',
    },
    'error.cost_center.too_many_fields': {
        'ru': 'максимальное число полей: {}, получено: {}',
    },
    'error.cost_center.too_few_fields': {
        'ru': 'минимальное число полей: {}, получено: {}',
    },
    'error.cost_center.too_many_active_fields': {
        'ru': 'максимальное число активных полей: {}, получено: {}',
    },
    'error.cost_center.too_few_active_fields': {
        'ru': 'минимальное число активных полей: {}, получено: {}',
    },
    'error.cost_center.too_long_field_title': {
        'ru': 'максимальная длина заголовка поля: {}, получено: {}',
    },
    'error.cost_center.too_short_field_title': {
        'ru': 'минимальная длина заголовка поля: {}, получено: {}',
    },
    'error.cost_center.too_long_value': {
        'ru': 'максимальная длина значения для поля "{}" — {}, а у вас {}',
    },
    'error.cost_center.too_many_field_values': {
        'ru': 'максимальное число значений для поля {}: {}, получено: {}',
    },
    'error.cost_center.too_few_field_values': {
        'ru': 'минимальное число значений для поля {}: {}, получено: {}',
    },
    'error.cost_center.creation_not_allowed': {
        'ru': 'для вашего аккаунта пока не разрешено создание новых ЦЗ',
    },
}
COST_CENTERS_RESTRICTIONS = {
    'cost_centers_max_count': 50,  #
    'total_fields_max_count': 50,  #
    'total_fields_min_count': 0,  #
    'active_fields_max_count': 5,  #
    'active_fields_min_count': 0,  #
    'field_title_max_length': 30,  #
    'field_title_min_length': 2,  #
    'field_value_max_length': 50,  #
    'field_values_max_count': 2000,
    'field_values_min_count': 1,
}


def build_error(response_key, response_param=None):
    error_dict = ERRORS[response_key]
    message = (
        error_dict['message'].format(response_param)
        if response_param
        else error_dict['message']
    )
    return {
        'code': error_dict['code'],
        'message': message,
        'errors': [{'code': error_dict['code'], 'text': message}],
    }


def prepare_xls(cost_centers):
    book = xlwt.Workbook()
    sheet = book.add_sheet('Test')
    for index, value in enumerate(cost_centers):
        sheet.write(index, 0, value)

    buf = io.BytesIO()
    book.save(buf)

    return buf.getvalue()


def remove_field(request_data: dict) -> None:
    request_data['field_settings'].pop()


def add_extra_field(request_data: dict) -> None:
    extra_field = dict(request_data['field_settings'][-1], title='Другое')
    extra_field.pop('id', None)
    request_data['field_settings'].append(extra_field)


def add_extra_field_hidden(request_data: dict) -> None:
    extra_field = dict(
        request_data['field_settings'][-1], title='Другое', hidden=True,
    )
    extra_field.pop('id', None)
    request_data['field_settings'].append(extra_field)


def reorder_fields(request_data: dict) -> None:
    field_settings = request_data['field_settings']
    field_settings[-2:] = field_settings[:-3:-1]


def change_field_title(request_data: dict) -> None:
    request_data['field_settings'][-1]['title'] += ' other'


def change_option_name(request_data: dict) -> None:
    request_data['name'] += ' other'


def duplicate_field_values(request_data: dict) -> None:
    request_data['field_settings'][-1]['values'] *= 2


def change_field_services(request_data: dict) -> None:
    request_data['field_settings'][-1]['services'].append('brand_new_service')
