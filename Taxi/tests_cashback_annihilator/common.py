import enum

CREATE_RESPONSE = 'create'
UPDATE_RESPONSE = 'update'
INVOICE_RESPONSE = 'invoice'


def is_any_exists_in_errors(iterable_to_exists, errors):
    return any([x for x in iterable_to_exists if x in errors])


class Error(enum.Enum):
    TRANSACTION_NOT_EXISTS = 'transaction_not_exists'

    CREATE_TRANSACTION_ERROR = 'create_transaction_error'
    UPDATE_TRANSACTION_ERROR = 'update_transaction_error'

    CREATE_BAD_REQUEST = 'create_bad_request'
    CREATE_RACE_CONDITION = 'create_race_condition'

    UPDATE_BAD_REQUEST = 'update_bad_request'
    UPDATE_NOT_FOUND = 'update_not_found'
    UPDATE_MATCH = 'update_match'

    @classmethod
    def _json_for_response_create(cls):
        return {
            cls.CREATE_TRANSACTION_ERROR: {
                'code': '500',
                'message': 'Unexpected error',
            },
            cls.CREATE_BAD_REQUEST: {'code': '400', 'message': 'Bad request'},
            cls.CREATE_RACE_CONDITION: {
                'code': '409',
                'message': 'Race condition',
            },
        }

    @classmethod
    def _json_for_response_update(cls):
        return {
            cls.UPDATE_TRANSACTION_ERROR: {
                'code': '500',
                'message': 'Unexpected error',
            },
            cls.UPDATE_BAD_REQUEST: {'code': '400', 'message': 'Bade request'},
            cls.UPDATE_NOT_FOUND: {'code': '404', 'message': 'Not found'},
            cls.UPDATE_MATCH: {'code': '409', 'message': 'Match failed'},
        }

    @classmethod
    def get_single_error(cls, errors, resp_type=CREATE_RESPONSE):
        all_errors = cls._json_for_response_create()
        if resp_type == UPDATE_RESPONSE:
            all_errors = cls._json_for_response_update()

        error = None
        for err in errors:
            error = all_errors.get(err, None)
        return error
