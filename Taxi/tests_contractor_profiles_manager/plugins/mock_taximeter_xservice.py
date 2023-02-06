import pytest


@pytest.fixture(name='mock_taximeter_xservice')
def _mock_taximeter_xservice(mockserver):
    class Context:
        def __init__(self):
            self.locale = 'ru'
            self.park_id = None
            self.contractor_profile_id = None
            self.status = None

        def set_data(
                self,
                locale=None,
                park_id=None,
                contractor_profile_id=None,
                status=None,
        ):
            if locale is not None:
                self.locale = locale
            if park_id is not None:
                self.park_id = park_id
            if contractor_profile_id is not None:
                self.contractor_profile_id = contractor_profile_id
            if status is not None:
                self.status = status

        @property
        def has_mock_calls(self):
            return exams_retrieve.has_calls

        def make_request(self):
            return {
                'locale': self.locale,
                'query': {
                    'park': {
                        'id': self.park_id,
                        'driver_profile': {'id': self.contractor_profile_id},
                    },
                },
            }

        def make_response(self):
            if self.status is None:
                return {}
            return {'dkvu_exam': {'pass': {'status': self.status}}}

    context = Context()

    @mockserver.json_handler(
        '/taximeter-xservice/utils/qc/driver/exams/retrieve',
    )
    def exams_retrieve(request):
        assert request.json == context.make_request()
        return context.make_response()

    return context
