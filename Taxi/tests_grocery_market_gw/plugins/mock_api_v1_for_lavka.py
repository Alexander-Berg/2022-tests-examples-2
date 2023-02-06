import pytest

# pylint: disable=unused-variable


@pytest.fixture(name='mock_api_v1_for_lavka')
def mock_api_v1_for_lavka(mockserver):
    class Context:
        def __init__(self):
            self.products = []
            self.banner_url = 'some-banner-url'
            self.results_url = 'some-results-url'

        def set_products(self, products):
            self.products = products

        def add_product(self, product):
            self.products.append(product)

        def set_banner_url(self, banner_url):
            self.banner_url = banner_url

        def set_results_url(self, results_url):
            self.results_url = results_url

    def handle_for_search(request, params):
        if 'text' not in params or 'gps' not in params:
            error = {
                'kind': 'ResolveSearchForLavkaError',
                'message': 'Required params is blank',
            }
            handler_result = {
                'handler': 'resolveSearchForLavka',
                'error': error,
            }
            return handler_result

        page = params['page'] if 'page' in params else 1
        count = params['count'] if 'count' in params else 5

        result = {
            'products': [],
            'bannerUrl': context.banner_url,
            'resultsUrl': context.results_url,
        }

        beg = (page - 1) * count
        end = min(beg + count, len(context.products))
        for i in range(beg, end):
            result['products'].append(context.products[i].get_data())

        handler_result = {'handler': 'resolveSearchForLavka', 'result': result}
        return handler_result

    @mockserver.json_handler('/market-api-grocery/api/v1')
    def mock_api_v1(request):
        assert 'name' in request.query
        handlers = request.query['name'].split(',')
        assert 'params' in request.json
        params = request.json['params']
        assert len(handlers) == len(params)
        response = {'results': []}
        for i, handler in enumerate(handlers):
            assert handler in [
                'resolveSearchForLavka',
            ]  # supported handlers list
            if handler == 'resolveSearchForLavka':
                response['results'].append(
                    handle_for_search(request, params[i]),
                )
            # other supported handling
        return mockserver.make_response(status=200, json=response)

    context = Context()
    return context
