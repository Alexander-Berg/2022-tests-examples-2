import pytest

TRANSLATIONS = pytest.mark.translations(
    client_messages={
        'scooters.screens.battery_exchange.screen_title': {
            'ru': 'Получение аккумуляторов',
        },
        'scooters.screens.battery_exchange.screen_title.for_return': {
            'ru': 'Сдача аккумуляторов',
        },
        'scooters.screens.battery_exchange.processed_counter': {
            'ru': 'получено',
        },
        'scooters.screens.battery_exchange.processed_counter.for_return': {
            'ru': 'сдано',
        },
        'scooters.screens.battery_exchange.to_process_counter': {
            'ru': 'осталось',
        },
        'scooters.screens.battery_exchange.to_process_counter.for_return': {
            'ru': 'осталось',
        },
        'scooters.screens.battery_exchange.processing_failed_count': {
            'ru': 'Не удалось получить',
        },
        (
            'scooters.screens.battery_exchange.processing_failed_count'
            '.for_return'
        ): {'ru': 'Не удалось сдать'},
        'scooters.screens.battery_exchange.open_door_button': {
            'ru': 'Получить аккумулятор',
        },
        'scooters.screens.battery_exchange.open_door_button.for_return': {
            'ru': 'Сдать аккумулятор',
        },
        'scooters.screens.battery_exchange.call_storekeeper': {
            'ru': 'Дуй к кладовщику',
        },
        'scooters.screens.battery_exchange.call_storekeeper.for_return': {
            'ru': 'Дуй к кладовщику чтобы сдать',
        },
        'scooters.screens.battery_exchange.open_failed_button': {
            'ru': 'Получить оставшиеся',
        },
        'scooters.screens.battery_exchange.open_failed_button.for_return': {
            'ru': 'Сдать оставшиеся',
        },
        'scooters.screens.battery_exchange.close_screen_button': {
            'ru': 'Все аккумуляторы получены',
        },
        'scooters.screens.battery_exchange.close_screen_button.for_return': {
            'ru': 'Все аккумуляторы сданы',
        },
        'scooters.screens.battery_exchange.processed_button': {
            'ru': 'Аккумулятор получен',
        },
        'scooters.screens.battery_exchange.processed_button.for_return': {
            'ru': 'Аккумулятор сдан',
        },
        'scooters.screens.battery_exchange.processing_failed_button': {
            'ru': 'Ячейка не открылась',
        },
        (
            'scooters.screens.battery_exchange.processing_failed_button'
            '.for_return'
        ): {'ru': 'Ячейка не открылась'},
        (
            'scooters.screens.battery_exchange.'
            'previous_accumulator_was_not_taken'
        ): {'ru': 'Заберите предыдущий аккумулятор'},
        (
            'scooters.screens.battery_exchange.'
            'previous_accumulator_was_not_returned'
        ): {'ru': 'Верните предыдущий аккумулятор'},
        'scooters.screens.battery_exchange.previous_cell_was_not_closed': {
            'ru': (
                'Одна из ячеек открыта. Закройте её перед открытием следующей'
            ),
        },
        'scooters.screens.battery_exchange.cell_is_broken': {
            'ru': 'Не смогли автоматически открыть ячейку',
        },
        'scooters.screens.battery_exchange.not_all_errors_resolved': {
            'ru': 'Кладовщик хреново работает. Надо лучше',
        },
        'scooters.battery_exchange.validation.not_all_pickuped': {
            'ru': 'Надо бы все таки забрать все аккумы',
        },
        'scooters.battery_exchange.validation.bad_request': {
            'ru': 'Какая-то ужасная ошибка',
        },
        (
            'scooters.battery_exchange.validation.scooter_accumulator'
            '.accumulator_was_not_taken'
        ): {'ru': 'Вы не забрали аккум. Заберите'},
        (
            'scooters.battery_exchange.validation.scooter_accumulator'
            '.cell_is_open'
        ): {'ru': 'Одна из ячеек открыта. Закройте её'},
        'scooters.battery_exchange.validation.not_all_returned': {
            'ru': 'Надо бы все таки вернуть все аккумы',
        },
        (
            'scooters.battery_exchange.validation.scooter_accumulator.'
            'accumulator_was_not_returned'
        ): {'ru': 'Вы не вернули аккум. Верните'},
        'scooters.battery_exchange.validation.telematics_problem_no_retry': {
            'ru': 'Очень страшная ошибка. Этот самокат лучше пропустить',
        },
        'scooters.battery_exchange.validation.same_battery_inserted': {
            'ru': 'Вставлена та же батарея',
        },
        'scooters.battery_exchange.validation.need_to_change_battery': {
            'ru': 'Брат, замени батарею',
        },
        'scooters.battery_exchange.validation.need_to_close_deck': {
            'ru': 'Брат, закрой деку',
        },
        'scooters.battery_exchange.validation.wait_sensor_update': {
            'ru': (
                'Информация о замененном аккумуляторе обновляется. '
                'Пожалуйста, подождите'
            ),
        },
        'scooters.battery_exchange.validation.low_battery_level': {
            'ru': (
                'Уровень заряда в замененном аккумуляторе %(level)s%. '
                'Вы точно заменили аккумулятор?'
            ),
        },
        'scooters.screens.shortcuts.qr_scan.title': {'ru': 'Сканировать'},
        'scooters.screens.shortcuts.qr_scan.subtitle': {
            'ru': 'QR-код на руле самоката',
        },
        'scooters.screens.shortcuts.support.title': {'ru': 'Поддержка'},
        'scooters.screens.battery_exchange.accumulator_was_not_taken': {
            'ru': 'Заберите аккумулятор',
        },
        'scooters.screens.battery_exchange.accumulator_was_not_returned': {
            'ru': 'Верните аккумулятор',
        },
        'scooters.screens.battery_exchange.cell_was_not_closed': {
            'ru': 'Закройте ячейку',
        },
        'scooters.screens.battery_exchange.cell_is_broken_for_validation': {
            'ru': 'Ячейка сломалась',
        },
        'scooters.screens.battery_exchange.reopen_door_button': {
            'ru': 'Открыть ячейку',
        },
        'scooters.screens.battery_exchange.reopen_door_button.for_return': {
            'ru': 'Открыть ячейку',
        },
        'scooters.screens.battery_exchange.common_error': {
            'ru': 'Случилось что-то странное',
        },
        'scooters.screens.battery_exchange.failed_cells_title': {
            'ru': 'Неоткрывшиеся ячейки',
        },
        'scooters.screens.battery_exchange.failed_cells.cell_title': {
            'ru': 'Ячейка %(cell_id)s',
        },
        'scooters.screens.battery_exchange.failed_cells.cell_subtitle': {
            'ru': 'Шкаф %(cabinet_id)s',
        },
        'scooters.battery_exchange.validation.tackles.not_pickuped': {
            'ru': 'Заберите снасть',
        },
        'scooters.battery_exchange.validation.tackles.not_returned': {
            'ru': 'Верните снасть',
        },
        (
            'scooters.battery_exchange.validation.tackles.'
            'recharging_wire.not_pickuped'
        ): {'ru': 'Заберите воскреситель'},
        (
            'scooters.battery_exchange.validation.tackles.'
            'recharging_wire.not_returned'
        ): {'ru': 'Верните воскреситель'},
        'scooters.claim.scooter_point_title': {
            'ru': 'Аккумулятор для самоката №%(number)s',
        },
        'scooters.claim.scooter_point_comment': {'ru': 'Самокат №%(number)s'},
        'scooters.claim.depot_point_title': {
            'ru': 'Возврат аккумуляторов в лавку',
        },
        'scooters.claim.depot_point_comment': {'ru': 'Лавка'},
        'scooters.vehicle_control.errors.incorrect_recharge_task': {
            'ru': 'Отсутствует задача или статус некорректен',
        },
        'scooters.vehicle_control.errors.incorrect_recharge_item.'
        'vehicle_isnot_assigned': {'ru': 'Целевой самокат не задан'},
        'scooters.vehicle_control.errors.incorrect_recharge_item': {
            'ru': 'Самокат не определен для данной задачи',
        },
        'scooters.claim.deadflow_comment': {'ru': 'Заказ на воскрешение'},
        'scooters.vehicle_control.errors.incorrect_request': {
            'ru': 'Некорректный запрос',
        },
        'scooters.vehicle_control.errors.incorrect_request.full': {
            'ru': 'Что-то пошло не так...',
        },
        'scooters.vehicle_control.errors.telematic_error': {
            'ru': 'Ошибка телематики',
        },
        'scooters.vehicle_control.errors.telematic_error.full': {
            'ru': 'Не удалось передать команду самокату',
        },
        'scooters.vehicle_control.errors.telematic_error'
        '.failed_to_open_lock': {'ru': 'Не удалось открыть замок'},
        'scooters.claim.recharge_comment': {
            'ru': 'Миссия на перезарядку самокатов',
        },
        'scooters.claim.relocate_comment': {
            'ru': 'Миссия на релокацию самокатов',
        },
        'scooters.claim.repair_comment': {'ru': 'Миссия на ремонт самокатов'},
        'scooters.claim.mixed_mission_comment': {'ru': 'Смешанная миссия'},
        'scooters.mission.flow_related_mission_tag.recharge': {
            'ru': 'перезарядка',
        },
        'scooters.mission.flow_related_mission_tag.relocate': {
            'ru': 'релокация',
        },
        'scooters.mission.flow_related_mission_tag.repair': {'ru': 'ремонт'},
        'scooters.pro.screens.address': {'ru': 'Адрес'},
        'scooters.pro.screens.help': {'ru': 'Помощь'},
        'scooters.pro.screens.confirm.default_button': {'ru': 'Подтвердить'},
        'scooters.pro.screens.confirm.cancel_button': {'ru': 'Отменить'},
        'scooters.pro.screens.confirm.arrive_at_point.title': {
            'ru': 'Точно приехал?',
        },
        'scooters.pro.screens.confirm.arrive_at_point.message': {
            'ru': 'Уехать нельзя, если однажды приехал',
        },
        'scooters.pro.screens.to_point.warehouse': {'ru': 'На склад'},
        'scooters.pro.screens.to_point.depot': {'ru': 'В лавку'},
        'scooters.pro.screens.to_point.parking': {'ru': 'На парковку'},
        'scooters.pro.screens.to_point.scooter': {'ru': 'К самокату'},
        'scooters.pro.screens.alert': {'ru': 'Опоздание'},
        'scooters.pro.screens.job.return_batteries': {
            'ru': 'Вернуть аккумчики',
        },
        'scooters.pro.screens.scooters': {'ru': 'Самокаты'},
        'scooters.pro.screens.quantity': {'ru': 'Количество %(amount)s'},
        'scooters.pro.screens.problems.didnt_open': {'ru': 'Не открылся'},
        'scooters.pro.screens.problems.not_found': {'ru': 'Не найден'},
        'scooters.pro.screens.problems.discharged': {'ru': 'Разряжен'},
        'scooters.pro.screens.confirm.finished_job.title': {
            'ru': 'Точно завершил?',
        },
        'scooters.pro.screens.confirm.finished_job.message': {
            'ru': 'Надо все сделать',
        },
        'scooters.pro.screens.finished_job.title': {'ru': 'Завершил'},
        'scooters.pro.screens.not_found': {'ru': 'Не найден'},
        'scooters.pro.screens.discharged': {'ru': 'Разряжен'},
        'scooters.pro.screens.didnt_open': {'ru': 'Не открылся'},
        'scooters.pro.screens.to_pickup': {'ru': 'Погрузить'},
        'scooters.pro.screens.on_board': {'ru': 'Погружен'},
        'scooters.pro.screens.completed': {'ru': 'Завершен заказ'},
        'scooters.pro.screens.scooters_relocated': {
            'ru': 'Скутеров обработано',
        },
        'scooters.pro.screens.order_time_title': {'ru': 'Время на заказ'},
        'scooters.pro.screens.job.pickup_vehicles': {'ru': 'Собрать самокаты'},
        'scooters.pro.screens.errors.title': {'ru': 'Ошибка'},
        'scooters.pro.screens.errors.wrong_scooter': {
            'ru': 'Отсканирован не тот самокат',
        },
        'scooters.pro.screens.errors.accumulator_pickup_failed': {
            'ru': 'Не получилось подтвердить выдачу аккумулятора',
        },
        'scooters.pro.screens.errors.accumulator_return_failed': {
            'ru': 'Не получилось подтвердить сдачу аккумулятора',
        },
        'scooters.pro.screens.errors.wrong_accumulator': {
            'ru': 'Отсканирован не тот аккумулятор',
        },
        'scooters.pro.screens.errors.scooter_already_processed': {
            'ru': 'Самокат уже отсканирован',
        },
        'scooters.pro.screens.errors.incorrect_request': {
            'ru': 'Что-то пошло не так...',
        },
        'scooters.pro.screens.job.dropoff_vehicles': {'ru': 'Разгрузка'},
        'scooters.pro.screens.to_dropoff': {'ru': 'Выгрузить'},
        'scooters.pro.screens.scooter_to_dropoff': {
            'ru': 'Самокат %(number)s',
        },
        'scooters.pro.screens.dropped_off': {'ru': 'Выгружен'},
        'scooters.relocation.validation.not_all_dropped_off': {
            'ru': 'Выгрузил меньше, чем нужно. Осталось %(quantity_left)s',
        },
        'scooters.relocation.validation.not_all_picked_up': {
            'ru': 'Загрузил не все',
        },
        'scooters.pro.screens.spent_time': {
            'ru': '%(hours)sч. %(minutes)sмин.',
        },
        'scooters.mission.status.created': {'ru': 'Создана'},
        'scooters.mission.status.preparing': {'ru': 'Подготовлена'},
        'scooters.mission.status.assigning': {'ru': 'Назначена'},
        'scooters.mission.status.performing': {'ru': 'Исполняется'},
        'scooters.mission.status.completed': {'ru': 'Завершена'},
        'scooters.mission.status.cancelling': {'ru': 'Отменена'},
        'scooters.mission.status.failed': {'ru': 'Провалена'},
        'scooters.mission.type.recharge': {'ru': 'Перезарядка'},
        'scooters.mission.type.resurrect': {'ru': 'Воскрешение'},
        'scooters.mission.type.relocation': {'ru': 'Релокация'},
        'scooters.point.type.scooter': {'ru': 'Самокат'},
        'scooters.point.type.depot': {'ru': 'Лавка'},
        'scooters.point.type.parking_place': {'ru': 'Парковка'},
        'scooters.point.status.created': {'ru': 'Создана'},
        'scooters.point.status.preparing': {'ru': 'Подготавливается'},
        'scooters.point.status.prepared': {'ru': 'Подготовлена'},
        'scooters.point.status.planned': {'ru': 'Запланирована'},
        'scooters.point.status.arrived': {'ru': 'Курьер прибыл'},
        'scooters.point.status.visited': {'ru': 'Посещена'},
        'scooters.point.status.skipped': {'ru': 'Пропущена'},
        'scooters.point.status.cancelled': {'ru': 'Отменена'},
        'scooters.job.status.created': {'ru': 'Создана'},
        'scooters.job.status.preparing': {'ru': 'Подготавливается'},
        'scooters.job.status.prepared': {'ru': 'Подготовлена'},
        'scooters.job.status.planned': {'ru': 'Запланирована'},
        'scooters.job.status.performing': {'ru': 'Исполняется'},
        'scooters.job.status.completed': {'ru': 'Выполнена'},
        'scooters.job.status.cancelled': {'ru': 'Отменена'},
        'scooters.job.status.failed': {'ru': 'Не удалась'},
        'scooters.job.type.pickup_batteries': {'ru': 'Взять аккумуляторы'},
        'scooters.job.type.return_batteries': {'ru': 'Вернуть аккумуляторы'},
        'scooters.job.type.battery_exchange': {'ru': 'Заменить аккумулятора'},
        'scooters.job.type.do_nothing': {'ru': 'Ничего'},
        'scooters.job.type.pickup_vehicles': {'ru': 'Забрать самокаты'},
        'scooters.job.type.dropoff_vehicles': {'ru': 'Выгрузить самокаты'},
        'scooters.mission_history.event_type.mission_created': {
            'ru': 'Миссия создана',
        },
        'scooters.mission_history.event_type.mission_status_updated': {
            'ru': 'Обновился статус миссии',
        },
        'scooters.mission_history.event_type.mission_started': {
            'ru': 'Миссия выполняется',
        },
        'scooters.mission_history.event_type.mission_completed': {
            'ru': 'Миссия завершена',
        },
        'scooters.mission_history.event_type.mission_cancelling': {
            'ru': 'Миссия отменяется',
        },
        'scooters.mission_history.event_type.point_arrived': {
            'ru': 'Курьер прибыл на точку',
        },
        'scooters.mission_history.event_type.point_completed': {
            'ru': 'Работы на точке завершены',
        },
        'scooters.mission_history.event_type.point_skipped': {
            'ru': 'Точка пропущена',
        },
        'scooters.mission_history.event_type.job_started': {
            'ru': 'Работа выполняется',
        },
        'scooters.mission_history.event_type.job_completed': {
            'ru': 'Работа завершена',
        },
        'scooters.mission_history.event_type.job_failed': {
            'ru': 'Работа не удалась',
        },
        'scooters.pro.screens.complete_mission': {'ru': 'Готово'},
        'scooters.pro.screens.job': {'ru': 'Работа'},
    },
)


DEEPLINKS_CONFIG = pytest.mark.config(
    SCOOTERS_OPS_TAXIMETER_DEEPLINKS={
        'telegram_support': 'chat',
        'scan_qr': (
            'scooters/scooter_qr_scanner?'
            'point_id={point_id}'
            '&job_id={job_id}'
            '&scooter_id={vehicle_id}'
            '&scooter_number={vehicle_number}'
        ),
        'diagnostics': (
            'scooters/scooter_diagnostics?'
            'point_id={point_id}'
            '&job_id={job_id}'
            '&scooter_id={vehicle_id}'
            '&scooter_number={vehicle_number}'
            '&selected={selected}'
        ),
        'complete_order': 'taximeter://scooters/complete_order',
        'battery_exchange_open_door': (
            'open_door/'
            'mission_id={mission_id}'
            '&cargo_point_id={cargo_point_id}'
            '&booking_id={booking_id}'
            '&job_type={job_type}'
        ),
        'battery_exchange_open_failed': (
            'open_failed/'
            'mission_id={mission_id}'
            '&cargo_point_id={cargo_point_id}'
            '&job_type={job_type}'
        ),
        'battery_exchange_processed': (
            'processed/'
            'mission_id={mission_id}'
            '&cargo_point_id={cargo_point_id}'
            '&booking_id={booking_id}'
            '&job_type={job_type}'
        ),
        'battery_exchange_processing_failed': (
            'processing_failed/'
            'mission_id={mission_id}'
            '&cargo_point_id={cargo_point_id}'
            '&booking_id={booking_id}'
            '&job_type={job_type}'
        ),
    },
)

TAGS_WITH_LOCK_CONFIG = pytest.mark.config(SCOOTERS_TAGS_WITH_LOCK=[])

SCOOTERS_PROBLEMS_CONFIG = pytest.mark.config(
    SCOOTERS_PROBLEMS={
        'not_found': {'tanker_key': 'scooters.pro.screens.not_found'},
        'discharged': {'tanker_key': 'scooters.pro.screens.discharged'},
        'didnt_open': {'tanker_key': 'scooters.pro.screens.didnt_open'},
    },
)

OLD_SCREENS_SETTINGS = pytest.mark.experiments3(
    name='scooters_ops_old_screens_settings',
    consumers=['scooters-ops/old-screens'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'ui_show_settings': [
            {
                'ui_element': 'processing_failed_button',
                'show_policies': ['not_to_show'],
            },
        ],
    },
    is_config=True,
)


DAP_HEADERS = {
    'Accept-Language': 'ru-ru',
    'X-Remote-IP': '127.0.0.1',
    'X-Request-Application-Version': '9.60 (1234)',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
}
