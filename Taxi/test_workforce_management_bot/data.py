SHIFTS = {
    'records': [
        {
            'shift': {
                'start': '2021-04-01T06:00:00+03:00',
                'duration_minutes': 390,
                'skill': 'lavka',
                'shift_id': 47246,
                'type': 'common',
                'breaks': [
                    {
                        'start': '2021-04-01T08:45:00+03:00',
                        'duration_minutes': 15,
                        'id': 7940,
                        'type': 'technical',
                    },
                ],
                'events': [
                    {
                        'event_id': 2,
                        'description': 'Обучение стрельбе',
                        'start': '2021-04-03T23:00:00+03:00',
                        'duration_minutes': 60,
                        'id': 3741,
                    },
                ],
            },
            'operator': {
                'login': 'abd-damir',
                'yandex_uid': '1130000003564500',
                'full_name': 'Новый Русский оператор',
                'revision_id': '2021-04-01T16:28:42.314606 +0000',
                'phone': '+1',
                'skills': ['lavka'],
            },
        },
    ],
}

ADDITIONAL_SHIFTS_JOBS = {
    'jobs': [
        {
            'job_id': 1,
            'job_status': 'completed',
            'shifts_distributed': 0,
            'job_data': {
                'datetime_from': '2021-08-02T02:00:00+03:00',
                'datetime_to': '2021-08-02T04:00:00+03:00',
                'skill': 'hokage',
                'additional_shifts_count': 1,
            },
        },
        {
            'job_id': 2,
            'job_status': 'completed',
            'shifts_distributed': 2,
            'job_data': {
                'datetime_from': '2021-09-03T10:00:00+03:00',
                'datetime_to': '2021-09-03T15:00:00+03:00',
                'skill': 'lavka',
                'additional_shifts_count': 3,
            },
        },
        {
            'job_id': 3,
            'job_status': 'completed',
            'shifts_distributed': 0,
            'job_data': {
                'datetime_from': '2021-10-05T12:00:00+03:00',
                'datetime_to': '2021-10-05T18:00:00+03:00',
                'skill': 'pokemon',
                'additional_shifts_count': 1,
            },
        },
    ],
}

ACCEPT_SHIFT_ERRORS = [
    {'code': 'candidate_not_found', 'message': 'candidate not found!!!'},
    {'code': 'busy_operator', 'message': 'busy operator!!!'},
    {'code': 'all_shifts_distributed', 'message': 'all shifts distributed!!!'},
    {'code': 'breaks_build_failed', 'message': 'breaks build failed!!!'},
    {'code': 'server_error', 'message': 'server error!!!'},
    {'code': 'some_unknown_error', 'message': 'some unknown error'},
]

DEFAULT_TRANSLATION = {
    'NewShifts': {'ru': 'У тебя изменились смены: {shifts}'},
    'Greetings': {
        'ru': 'Регистрация прошла успешно, показываю меню {emoji_heart}!',
    },
    'SingleShiftEvent': {'ru': '{description} {period}'},
    'SingleShift': {
        'ru': '{emoji_calendar} {shift_type} {period} {shift_events}',
    },
    'ShiftEventsTitle': {
        'ru': 'Обрати внимание, на смену запланировано: {shift_events_list}',
    },
    'CommonShiftTitle': {'ru': 'Смена'},
    'AdditionalShiftOffer': {
        'ru': (
            'Тебе предложена дополнительная смена: {emoji_calendar} {period}'
        ),
    },
    'TooManyOperators': {
        'ru': 'К этому аккаунту привязано больше одного оператора',
    },
    'MyShifts': {'ru': 'Ближайшие смены: {shifts}'},
    'MyBreaks': {'ru': 'Смена сегодня {period}: {breaks}'},
    'SingleTechnicalBreak': {'ru': '{emoji_coffee} Перерыв {period}'},
    'OfferDomain': {'ru': 'Домен {domain}'},
    'NextShift': {
        'ru': 'На данный момент у тебя нет смены. Ближайшая смена {period}',
    },
    'ShiftOfferButtonText': {'ru': 'Смена {period}'},
    'ShiftOfferTitle': {'ru': 'Вам предложены доп. смены:'},
    'AdditionalShiftOfferEmpty': {
        'ru': 'Вам не предложено ни одной доп. смены',
    },
    'ConfirmChoiceRequest': {
        'ru': 'Вы уверены, что хотите выйти в данную смену?',
    },
    'ChoiceConfirmed': {'ru': 'Доп. смена выбрана успешно'},
    'ChoiceCancelled': {'ru': 'Ваш выбор отменен'},
    'Accept': {'ru': 'Принять'},
    'Reject': {'ru': 'Отказать'},
    'CandidateNotFound': {'ru': 'Такой кандидат на доп. смену не найден'},
    'BusyOperator': {'ru': 'У вас есть другие смены в период доп. смены'},
    'AllShiftsDistributed': {
        'ru': 'Извините, все доступные доп. смены распределены',
    },
    'BreaksBuildFailed': {'ru': 'Не удалось расставить перерывы'},
    'DefaultMessage': {'ru': 'Ошибка сервера'},
    'Reregister': {'ru': 'aaa'},
}
