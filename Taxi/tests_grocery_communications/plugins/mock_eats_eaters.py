import pytest


@pytest.fixture(name='eats_eaters')
def mock_eats_eaters(mockserver):
    class Context:
        def __init__(self):
            self.eats_id = None
            self.with_soft_deleted = None

            self.check_request_flag = False

        def check_request(self, *, eats_id=None, with_soft_deleted=None):
            self.eats_id = eats_id
            self.with_soft_deleted = with_soft_deleted

            self.check_request_flag = True

        def times_find_by_id_called(self):
            return mock_find_by_id.times_called

    context = Context()

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def mock_find_by_id(request):
        if context.check_request_flag:
            body = request.json
            if context.eats_id is not None:
                assert body['id'] == context.eats_id
            if context.with_soft_deleted is not None:
                assert body['with_soft_deleted'] == context.with_soft_deleted

        return {
            'eater': {
                'id': 'taxi:213u9dm912e321d',
                'uuid': 'test_uuid',
                'created_at': '2019-12-31T10:59:59+03:00',
                'updated_at': '2019-12-31T10:59:59+03:00',
            },
        }

    return context
