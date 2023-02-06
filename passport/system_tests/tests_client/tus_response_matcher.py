from hamcrest import has_entries
from hamcrest.core.base_matcher import BaseMatcher


class TusResponseMatcher(BaseMatcher):
    def __init__(self, status, expected_entries):
        self.expected_status = status
        self.expected_entries = expected_entries
        self.mismatch_message = ''

    def _matches(self, response):
        if response.status_code != self.expected_status:
            self.mismatch_message = 'Код ответа не {expected}: {actual}\n'.format(
                expected=self.expected_status,
                actual=response.status_code
            )
            return False
        return has_entries(self.expected_entries).matches(response.json())

    def describe_mismatch(self, response, mismatch_description):
        mismatch_description.append_text(self.mismatch_message)
        has_entries(self.expected_entries).describe_mismatch(response.json(), mismatch_description)

    def describe_to(self, description):
        description.append_text('Ответ совпадает: ')
        has_entries(self.expected_entries).describe_to(description)


def is_ok_response(expected_entries=None):
    if not expected_entries:
        expected_entries = {}
    expected_entries['status'] = 'ok'
    return TusResponseMatcher(200, expected_entries)


def is_tus_error(error, error_description):
    expected = {
        'error': error,
        'error_description': error_description,
    }
    return TusResponseMatcher(400, expected)
