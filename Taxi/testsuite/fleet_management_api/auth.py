from . import utils

OPTEUM_SERVICE_ID = 'opteum'

DAC_MOCK_URL = '/dispatcher-access-control/v1/parks/users/yandex/grants/list'

USER_TICKET_HEADER = 'X-Ya-User-Ticket'
USER_TICKET = '_!fake!_ya-54591353'

USER_TICKET_PROVIDER_HEADER = 'X-Ya-User-Ticket-Provider'
USER_TICKET_PROVIDER = 'yandex'

USER_TICKET_HEADERS = {
    USER_TICKET_HEADER: USER_TICKET,
    USER_TICKET_PROVIDER_HEADER: USER_TICKET_PROVIDER,
}

HEADERS = {**USER_TICKET_HEADERS, **utils.X_REAL_IP_HEADERS}


def check_user_ticket_headers(headers):
    utils.check_headers(headers, USER_TICKET_HEADERS)
