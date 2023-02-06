def make_error(code, message):
    return {'code': code, 'message': message}


PARK_NOT_FOUND = make_error('404', 'park was not found')
CONTRACTOR_NOT_FOUND = make_error('404', 'contractor was not found')
OFFER_NOT_ACCEPTED = make_error('403', 'offer was not accepted')
