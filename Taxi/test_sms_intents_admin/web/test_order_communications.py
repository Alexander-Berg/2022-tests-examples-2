import pytest


YQL_RESULTS_BY_OPERATION_ID = {
    'order_1_sms': 'sms.json',
    'order_1_push': 'push.json',
    'order_1_push_status': 'push_status.json',
    'order_1_yasms': 'yasms.json',
}


def yql_results(operation_id, load_json):
    return load_json(YQL_RESULTS_BY_OPERATION_ID[operation_id])


@pytest.fixture
def _patch_yql_operations(patch, load_json):
    @patch('yql.api.v1.client.YqlClient')
    def _yql_client(*args, **kwargs):
        class YqlClient:
            class YQLRequest:
                json = {}

                @classmethod
                def run(cls):
                    pass

                @property
                def operation_id(self):
                    return self._operation_id

                def __init__(self, operation_id):
                    self._operation_id = operation_id

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def __init__(self):
                self._operation_id = None

            def query(self, *args, **kwarg):
                self._operation_id = kwarg['title']
                return self.YQLRequest(self._operation_id)

        return YqlClient()

    @patch('yql.client.operation.YqlOperationStatusRequest')
    def _yql_operation_status_request(operation_id):
        class YQLRequest:
            status = 'COMPLETED'
            json = {}

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlAbortOperationRequest')
    def _yql_operation_abort_request(operation_id):
        class YQLRequest:
            json = {}

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlOperationShareIdRequest')
    def _yql_operation_share_id_request(op_id):
        class YQLRequest:
            json = 'public_link'

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlOperationResultsRequest')
    def _yql_operation_results_request(operation_id):
        class YQLRequest:
            json = {}

            def run(self):
                pass

            def get_results(self):
                class Result:
                    def __init__(self):
                        results = yql_results(operation_id, load_json)
                        self.rows = results['rows']
                        self.column_names = results['columns']

                    def fetch_full_data(self):
                        return self.rows

                return [Result()]

        return YQLRequest()


@pytest.mark.now('2022-02-01T12:00:00+0000')
@pytest.mark.parametrize(
    'date',
    ['bad1', '2022-02-01', '2022-03-01', '2021-03-01'],
    ids=['bad', 'today', 'future', 'too_old'],
)
async def test_bad_dates(web_app_client, date):
    response = await web_app_client.get(
        '/v1/order/communications',
        params={'order_id': 'order_1', 'date': date},
    )
    assert response.status == 400


@pytest.mark.now('2022-02-01T12:00:00+0000')
@pytest.mark.usefixtures('_patch_yql_operations')
async def test_get_order_communications(web_app_client, mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _mock_personal_phones_find(request):
        return {'id': 'personal_id', 'value': '+79997771223'}

    response = await web_app_client.get(
        '/v1/order/communications',
        params={'order_id': 'order_1', 'date': '2022-01-13'},
    )

    assert response.status == 200
    content = await response.json()

    assert content == {
        'status': 'completed',
        'message': 'All operations completed',
        'communications': [
            {
                'created': '2022-01-13T10:44:27+0300',
                'status': 'sent',
                'recipient': {
                    'go_user_id': '2f7a22135fd7a918aec15c09ea75b991',
                },
                'message': {
                    'message_id': '0d2bae3bed2b480c910d9841a28a55a1',
                    'channel': 'push',
                    'issuer_service': 'order-notify',
                },
                'payload': {'intent': 'taxi_order_corpweb_on_assigned_taxi'},
                'status_history': [
                    {'status': 'sent', 'created': '2022-01-13T10:44:27+0300'},
                    {
                        'status': 'expired',
                        'created': '2022-01-13T10:44:48+0300',
                    },
                ],
                'provider': {
                    'name': 'xiva',
                    'message_id': 'RiVZu5tW4mI1',
                    'meta': {},
                },
            },
            {
                'created': '2022-01-13T10:47:01+0300',
                'status': 'sent',
                'recipient': {
                    'go_user_id': '2f7a22135fd7a918aec15c09ea75b991',
                },
                'message': {
                    'message_id': 'd2ec63f7b36e4a4784fc33cd26282bc5',
                    'channel': 'push',
                    'issuer_service': 'order-notify',
                },
                'payload': {'intent': 'taxi_order_corpweb_on_waiting_taxi'},
                'status_history': [
                    {'status': 'sent', 'created': '2022-01-13T10:47:01+0300'},
                    {
                        'status': 'expired',
                        'created': '2022-01-13T10:47:18+0300',
                    },
                ],
                'provider': {
                    'name': 'xiva',
                    'message_id': 'xkVuSARR5a61',
                    'meta': {},
                },
            },
            {
                'created': '2022-01-13T10:44:48+0300',
                'status': 'sent',
                'recipient': {
                    'go_user_id': '',
                    'personal_phone_id': 'personal_id',
                },
                'message': {
                    'message_id': 'dd5e1b8b658542918374461c810395aa',
                    'channel': 'sms',
                    'issuer_service': '',
                },
                'payload': {
                    'intent': 'taxi_order_corpweb_on_assigned_taxi',
                    'text': 'Taxi paid for you: ya.cc/3BB8T',
                },
                'status_history': [
                    {
                        'status': 'enqueued',
                        'created': '2022-01-13T10:44:48+0300',
                    },
                    {
                        'status': 'deliveredtosmsc',
                        'created': '2022-01-13T10:44:49+0300',
                    },
                    {
                        'status': 'sent_to_gate',
                        'created': '2022-01-13T10:44:49+0300',
                    },
                    {
                        'status': 'senttosmsc',
                        'created': '2022-01-13T10:44:49+0300',
                    },
                ],
                'provider': {
                    'name': 'yasms',
                    'message_id': '2055000383402779',
                    'meta': {'gate': '69'},
                },
            },
            {
                'created': '2022-01-13T10:47:18+0300',
                'status': 'sent',
                'recipient': {
                    'go_user_id': '',
                    'personal_phone_id': 'personal_id',
                },
                'message': {
                    'message_id': '1803bf5892f5478e8769b391b47eb601',
                    'channel': 'sms',
                    'issuer_service': '',
                },
                'payload': {
                    'intent': 'taxi_order_corpweb_on_waiting_taxi',
                    'text': 'Driver on waiting. Blue Kia Rio',
                },
                'status_history': [
                    {
                        'status': 'enqueued',
                        'created': '2022-01-13T10:47:18+0300',
                    },
                    {
                        'status': 'deliveredtosmsc',
                        'created': '2022-01-13T10:47:19+0300',
                    },
                    {
                        'status': 'sent_to_gate',
                        'created': '2022-01-13T10:47:19+0300',
                    },
                    {
                        'status': 'senttosmsc',
                        'created': '2022-01-13T10:47:19+0300',
                    },
                ],
                'provider': {
                    'name': 'yasms',
                    'message_id': '2055000383405712',
                    'meta': {'gate': '69'},
                },
            },
        ],
    }
