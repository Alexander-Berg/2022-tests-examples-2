HEADERS_KEYS = (
    'report.users.name',
    'report.users.phone',
    'report.users.email',
    'report.users.id',
    'report.users.cost_center',
    'report.users.status',
    'report.users.role',
    'report.users.limit',
    'report.users.spent',
    'report.users.classes',
    'report.department',
    'report.department_path',
)

HEADERS_CABINET_KEYS = (
    'report.users.name',
    'report.users.phone',
    'report.users.email',
    'report.users.id',
    'report.users.status',
    'report.department',
    'report.users.limit_taxi_sum',
    'report.users.limit_drive_sum',
    'report.users.limit_eats2_sum',
    'report.users.limit_tanker_sum',
    'report.users.cost_center',
)

HEADERS_OLD_CC_KEYS = (
    'report.users.cost_centers_rules',
    'report.users.cost_centers_values',
)
HEADERS_NEW_CC = (
    'Настройки центров затрат',
    'Центр затрат',
    'Цель поездки',
    'Номер бонусной карты',
)
HEADERS_NEW_CC_EN = ('Cost centers settings',) + HEADERS_NEW_CC[1:]
CORP_TRANSLATIONS = {
    'report.users.active': {'ru': 'Активен', 'en': 'Active'},
    'report.users.inactive': {'ru': 'Неактивен', 'en': 'Inactive'},
    'report.report': {'ru': 'Отчёт', 'en': 'Report'},
    'report.users.company': {'ru': 'Компания', 'en': 'Company'},
    'report.users.created_date': {
        'ru': 'Дата создания отчёта',
        'en': 'Report creation date',
    },
    'report.users.name': {'ru': 'Имя пользователя', 'en': 'User\'s name'},
    'report.users.email': {'ru': 'Электронная почта', 'en': 'Email'},
    'report.users.id': {'ru': 'ID сотрудника', 'en': 'Employee ID'},
    'report.users.cost_center': {'ru': 'Центр затрат', 'en': 'Cost center'},
    'report.users.status': {
        'ru': 'Статус сотрудника',
        'en': 'Employee status',
    },
    'report.users.role': {'ru': 'Группа', 'en': 'Group'},
    'report.users.limit': {'ru': 'Лимит', 'en': 'Limit'},
    'report.users.limit_taxi_sum': {'ru': 'Лимит такси', 'en': 'Limit taxi'},
    'report.users.limit_drive_sum': {
        'ru': 'Лимит драйва',
        'en': 'Limit drive',
    },
    'report.users.limit_eats2_sum': {'ru': 'Лимит еды', 'en': 'Limit eats'},
    'report.users.limit_tanker_sum': {
        'ru': 'Лимит заправок',
        'en': 'Limit tanker',
    },
    'report.users.spent': {
        'ru': 'Потрачено в текущем месяце',
        'en': 'Spent this month',
    },
    'report.users.classes': {
        'ru': 'Доступные тарифы',
        'en': 'Available service classes',
    },
    'report.department': {'ru': 'Подразделение', 'en': 'Department'},
    'report.department_path': {
        'ru': 'Цепочка подразделений',
        'en': 'Department hierarchy',
    },
    'report.users.cost_centers_rules': {
        'ru': 'Настройка центров затрат',
        'en': 'Cost center settings',
    },
    'report.users.cost_centers_values': {
        'ru': 'Список центров затрат',
        'en': 'List of cost centers',
    },
    'role.cabinet_only_name': {
        'ru': 'Без права самостоятельного заказа',
        'en': 'Without ordering privileges',
    },
    'report.users.phone': {'ru': 'Телефон', 'en': 'Phone'},
    # 'report': {'ru': 'Телефон', 'en': 'Phone'},
    'report.users.cost_centers_options': {
        'ru': 'Настройки центров затрат',
        'en': 'Cost centers settings',
    },
    'report.users.cost_centers_format_mixed': {
        'ru': 'смешанный',
        'en': 'mixed',
    },
    'report.users.cost_centers_format_select': {
        'ru': 'выбор из списка',
        'en': 'select from list',
    },
    'report.users.cost_centers_format_text': {
        'ru': 'ввод вручную',
        'en': 'simple text',
    },
    'report.users.cost_centers_required': {
        'ru': 'обязателен',
        'en': 'required',
    },
    'report.users.cost_centers_not_required': {
        'ru': 'необязателен',
        'en': 'not required',
    },
    'report.users.cost_centers_values_exist': {'ru': 'да', 'en': 'yes'},
    'report.users.cost_centers_values_dont_exist': {'ru': 'нет', 'en': 'no'},
}
TARIFF_TRANSLATIONS = {
    'econom': {'ru': 'Эконом', 'en': 'Econom'},
    'business': {'ru': 'Комфорт', 'en': 'Comfort'},
    'start': {'ru': 'Старт', 'en': 'Start'},
}

HEADERS = tuple(CORP_TRANSLATIONS[header]['ru'] for header in HEADERS_KEYS)
HEADERS_CABINET = tuple(
    CORP_TRANSLATIONS[header]['ru'] for header in HEADERS_CABINET_KEYS
)

HEADERS_EN = tuple(CORP_TRANSLATIONS[header]['en'] for header in HEADERS_KEYS)
HEADERS_OLD_CC = tuple(
    CORP_TRANSLATIONS[header]['ru'] for header in HEADERS_OLD_CC_KEYS
)
DEFAULT_CC_COLUMN_VALUES = (
    'Основной',
    'смешанный, обязателен',
    'смешанный, обязателен',
    'ввод вручную, обязателен',
)
DEFAULT_CC_COLUMN_VALUES_EN = (
    'Основной',
    'mixed, required',
    'mixed, required',
    'simple text, required',
)
OTHER_CC_COLUMN_VALUES = (
    'Запасной',
    'выбор из списка, обязателен',
    'смешанный, необязателен',
    'ввод вручную, необязателен',
)
OTHER_CC_COLUMN_VALUES_EN = (
    'Запасной',
    'select from list, required',
    'mixed, not required',
    'simple text, not required',
)
EMPTY_CELL = ''


def empty_cells(count: int) -> tuple:
    return (EMPTY_CELL,) * count


def _translate(key_part, locale):
    return CORP_TRANSLATIONS[f'report.{key_part}'][locale]


def get_headers_cells(
        headers,
        report_date='2018-09-17',
        company='Yandex.Taxi team',
        department=None,
        department_path=None,
        locale='ru',
):
    _empty_cells = empty_cells(len(headers) - 3)
    result = [
        (_translate('users.company', locale), '', company) + _empty_cells,
    ]
    if department is not None:
        result.append(
            (_translate('department', locale), '', department) + _empty_cells,
        )
    if department_path is not None:
        result.append(
            (_translate('department_path', locale), '', department_path)
            + _empty_cells,
        )
    result.append(
        (_translate('users.created_date', locale), '', report_date)
        + _empty_cells,
    )
    result.append(empty_cells(len(headers)))
    result.append(headers)
    return result
