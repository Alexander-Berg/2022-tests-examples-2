import pytest

import testsuite


def _build_cursor(i):
    return {'mock_cursor': str(i)}


def _get_cursor_pos(cursor):
    return int(cursor['mock_cursor'])


class _Context:
    def __init__(self):
        self.schedules_updates = None
        self.docs = []

    def set_docs(self, docs):
        self.docs = docs

    def handle_schedules_updates(self, request_body):
        cursor = request_body.get('cursor', None)
        limit = request_body.get('limit', 100)

        from_ = 0 if cursor is None else _get_cursor_pos(cursor)
        to_ = min(from_ + limit, len(self.docs))

        schedules = self.docs[from_:to_]
        next_cursor = _build_cursor(to_) if to_ < len(self.docs) else None

        response = {'schedules': schedules}

        if next_cursor:
            response['next_cursor'] = next_cursor

        return response

    def get_schedules_updates_calls(self):
        result = []
        try:
            while True:
                next_call = self.schedules_updates.next_call()
                result.append(next_call['request'].json)
        except testsuite.utils.callinfo.CallQueueEmptyError:
            pass
        return result


@pytest.fixture(name='mock_bsx')
def mock_bsx(mockserver):
    ctx = _Context()

    @mockserver.json_handler('/billing-subventions-x/v2/schedules/updates')
    def schedules_updates(request):
        return ctx.handle_schedules_updates(request.json)

    ctx.schedules_updates = schedules_updates

    return ctx
