import pytest


class SelfregContext:
    def __init__(self):
        self.error_code = None
        self.selfreg_type = None
        self.mock_tags = None
        self.selfreg_id = 'selfreg_id'
        self.city_id = 'city_id'
        self.country_id = 'country_id'
        self.phone_pd_id = 'phone_pd_id'

    def set_selfreg(
            self,
            selfreg_type=None,
            mock_tags=None,
            selfreg_id='selfreg_id',
            city_id='city_id',
            country_id='country_id',
            phone_pd_id='phone_pd_id',
    ):
        self.selfreg_type = selfreg_type
        self.selfreg_id = selfreg_id
        self.city_id = city_id
        self.country_id = country_id
        self.phone_pd_id = phone_pd_id
        self.mock_tags = mock_tags

    def set_error_code(self, code=500):
        self.error_code = code


@pytest.fixture(name='selfreg', autouse=True)
def _selfreg_service(mockserver):
    context = SelfregContext()

    @mockserver.json_handler('/selfreg/internal/selfreg/v1/validate')
    def _validate_token(request):
        if context.error_code:
            return mockserver.make_response(status=context.error_code)
        result = {
            'city_id': context.city_id,
            'selfreg_id': context.selfreg_id,
            'country_id': context.country_id,
            'phone_pd_id': context.phone_pd_id,
        }
        if context.selfreg_type is not None:
            result['selfreg_type'] = context.selfreg_type
        if context.mock_tags is not None:
            result['mock_tags'] = context.mock_tags
        return result

    return context
