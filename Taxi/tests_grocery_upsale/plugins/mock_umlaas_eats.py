import pytest


@pytest.fixture(name='umlaas_eats', autouse=True)
def mock_grocery_upsale(mockserver):
    class Context:
        def __init__(self):
            self._upsale_ids = []
            self._throw_error = False

        def add_product(self, product_id: str):
            self._upsale_ids.append(product_id)

        def add_products(self, products: list):
            self._upsale_ids.extend(products)

        def set_response_type(self, *, is_error=None, error_on_source=None):
            self._throw_error = is_error

        @property
        def upsale_ids(self):
            return self._upsale_ids

        @property
        def throw_error(self):
            return self._throw_error

        @property
        def umlaas_called(self):
            return umlaas_handler.times_called

    context = Context()

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/grocery-suggest')
    def umlaas_handler(request):
        assert request.args['suggest_type'] == 'complement-items'
        assert request.args['service_name'] == 'grocery-upsale'
        assert request.args['request_source'] == 'menu-page'

        if context.throw_error:
            return mockserver.make_response('Error 500', status=500)

        return {
            'exp_list': [],
            'request_id': request.args['request_id'],
            'items': [
                {'product_id': upsale_id} for upsale_id in context.upsale_ids
            ],
        }

    return context
