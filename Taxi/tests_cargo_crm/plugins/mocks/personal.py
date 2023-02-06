import pytest


@pytest.fixture(name='personal_ctx')
def _personal_ctx(mockserver):
    class Context:
        def __init__(self):
            self._by_id = {'phones': {}, 'emails': {}, 'yandex_logins': {}}
            self._by_value = {key: dict() for key in self._by_id}

            self.store_response = None
            self.find_response = None
            self.retrieve_response = None
            self.bulk_retrieve_response = None

        def set_phones(self, phone_values):
            self._set_values('phones', phone_values)

        def set_emails(self, email_values):
            self._set_values('emails', email_values)

        def get_retrieve_response(self, request, data_type):
            if self.retrieve_response is not None:
                return self.retrieve_response

            pd_id = request.json['id']
            if pd_id not in self._by_id[data_type]:
                respbody = {'code': '404', 'message': 'not found'}
                return mockserver.make_response(status=404, json=respbody)

            value = self._by_id[data_type][pd_id]
            respbody = {'id': pd_id, 'value': value}
            return mockserver.make_response(status=200, json=respbody)

        def get_store_response(self, request, data_type):
            if callable(self.store_response):
                # because of false positive
                # pylint: disable=E1102
                return self.store_response(request, data_type)

            if self.store_response is not None:
                return self.store_response

            value = request.json['value']
            pd_id = self._by_value[data_type].get(value, 'lost_id')

            respbody = {'id': pd_id, 'value': value}

            return mockserver.make_response(status=200, json=respbody)

        def get_find_response(self, request, data_type):
            if self.find_response is not None:
                return self.find_response

            value = request.json['value']
            pd_id = self._by_value[data_type].get(value)
            if pd_id is None:
                respbody = {'code': '404', 'message': 'not found'}
                return mockserver.make_response(status=404, json=respbody)

            respbody = {'id': pd_id, 'value': value}
            return mockserver.make_response(status=200, json=respbody)

        def get_bulk_retrieve_response(self, request, data_type):
            if self.bulk_retrieve_response is not None:
                return self.bulk_retrieve_response

            respbody = {'items': []}
            for pd_id, value in self._by_id[data_type].items():
                respbody['items'].append({'id': pd_id, 'value': value})

            return mockserver.make_response(status=200, json=respbody)

        def _set_values(self, data_type, values):
            self._by_id[data_type] = {}
            self._by_value[data_type] = {}
            for item in values:
                pd_id = item['id']
                value = item['value']
                self._by_value[data_type][value] = pd_id
                self._by_id[data_type][pd_id] = value

    return Context()


@pytest.fixture(name='personal_handler_retrieve')
def _personal_handler_retrieve(mockserver, personal_ctx):
    url = r'/personal/v1/(?P<data_type>\w+)/retrieve'

    @mockserver.json_handler(url, regex=True)
    def handler(request, data_type):
        return personal_ctx.get_retrieve_response(request, data_type)

    return handler


@pytest.fixture(name='personal_handler_store')
def _personal_handler_store(mockserver, personal_ctx):
    url = r'/personal/v1/(?P<data_type>\w+)/store'

    @mockserver.json_handler(url, regex=True)
    def handler(request, data_type):
        return personal_ctx.get_store_response(request, data_type)

    return handler


@pytest.fixture(name='personal_handler_find')
def _personal_handler_find(mockserver, personal_ctx):
    url = r'/personal/v1/(?P<data_type>\w+)/find'

    @mockserver.json_handler(url, regex=True)
    def handler(request, data_type):
        return personal_ctx.get_find_response(request, data_type)

    return handler


@pytest.fixture(name='personal_handler_bulk_retrieve')
def _personal_handler_bulk_retrieve(mockserver, personal_ctx):
    url = r'/personal/v1/(?P<data_type>\w+)/bulk_retrieve'

    @mockserver.json_handler(url, regex=True)
    def handler(request, data_type):
        return personal_ctx.get_bulk_retrieve_response(request, data_type)

    return handler


@pytest.fixture(name='personal_mocks')
def _personal_mocks(mockserver):
    class Handlers:
        @staticmethod
        @mockserver.json_handler('/personal/v1/yandex_logins/store')
        def _yandex_logins_store(request):
            return {
                'id': request.json['value'] + '_id',
                'value': request.json['value'],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/yandex_logins/bulk_retrieve')
        def _mock_bulk_retrieve_yandex_logins(request):
            return {
                'items': [
                    {
                        'id': x['id'],
                        'value': x['id'][:-3] if len(x['id']) > 3 else '',
                    }
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/yandex_logins/retrieve')
        def _yandex_logins_retrieve(request):
            pd_id = request.json['id']
            return {'id': pd_id, 'value': pd_id[:-3] if len(pd_id) > 3 else ''}

        @staticmethod
        @mockserver.json_handler('/personal/v1/emails/store')
        def _emails_store(request):
            return {
                'id': request.json['value'] + '_id',
                'value': request.json['value'],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/store')
        def _phones_store(request):
            return {
                'id': request.json['value'] + '_id',
                'value': request.json['value'],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/bulk_store')
        def _mock_bulk_store_phones(request):
            return {
                'items': [
                    {'id': x['value'] + '_id', 'value': x['value']}
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/emails/bulk_store')
        def _mock_bulk_store_emails(request):
            return {
                'items': [
                    {'id': x['value'] + '_id', 'value': x['value']}
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
        def _mock_bulk_retrieve_phones(request):
            return {
                'items': [
                    {
                        'id': x['id'],
                        'value': x['id'][:-3] if len(x['id']) > 3 else '',
                    }
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/retrieve')
        def _mock_retrieve_phone(request):
            pd_id = request.json['id']
            return {'id': pd_id, 'value': pd_id[:-3] if len(pd_id) > 3 else ''}

        @staticmethod
        @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
        def _mock_bulk_retrieve_emails(request):
            return {
                'items': [
                    {
                        'id': x['id'],
                        'value': x['id'][:-3] if len(x['id']) > 3 else '',
                    }
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/emails/retrieve')
        def _emails_retrieve(request):
            pd_id = request.json['id']
            return {'id': pd_id, 'value': pd_id[:-3] if len(pd_id) > 3 else ''}

    return Handlers()
