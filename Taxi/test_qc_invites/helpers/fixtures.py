TEST_INVITE_SUCCESS_BODY = [
    (
        {
            'media': ['back', 'front', 'side'],
            'sanctions': ['orders_off'],
            'filters': {'license_number': '777', 'park_id': '999'},
            'comment': 'Комментарий',
        },
    ),
    (
        {
            'media': ['back', 'front', 'side'],
            'sanctions': ['orders_off'],
            'filters': {'license_pd_id': '666', 'park_id': '999'},
            'comment': 'Комментарий',
        },
    ),
]

TEST_INVITE_SUCCESS_EXAM = [('dkk',), ('dkvu',)]

TEST_INVITE_INFO_BODY = [
    (
        {
            'exam': 'dkk',
            'sanctions': ['orders_off'],
            'filters': {'car_number': 'x124yy777'},
            'comment': 'Комментарий',
        },
    ),
]

TEST_FULL_SERVICE_ROUTE_BODY = [
    (
        {
            'sanctions': ['orders_off'],
            'filters': {'car_number': 'x124yy777'},
            'comment': 'Комментарий',
        },
    ),
]

TEST_FULL_SERVICE_ROUTE_EXAM = [('dkk',)]
