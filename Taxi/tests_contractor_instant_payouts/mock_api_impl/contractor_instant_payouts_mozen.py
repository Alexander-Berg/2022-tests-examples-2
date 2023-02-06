NAME = 'contractor-instant-payouts-mozen'


def _handler_api_sbp_members(context, mockserver):
    def handler(request):
        return [
            {
                'id': 1,
                'member_id': '100000000008',
                'name': 'Alfa Bank',
                'name_rus': 'Альфа Банк',
            },
            {
                'id': 2,
                'member_id': '200000000008',
                'name': 'Tinkoff Bank',
                'name_rus': 'Тинькофф Банк',
            },
        ]

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add(
        '/api/public/sbp/members',
        _handler_api_sbp_members(context, mockserver),
    )

    return mocks
