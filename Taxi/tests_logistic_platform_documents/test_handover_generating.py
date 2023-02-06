import pytest
COMON_STQ_PARAMS = {'employer_code': 'some_employer'}


class LogisticPlatformRequestGetMocker:
    def __init__(self) -> None:
        self.data = {
            'request1': 'data1',
            'request2': 'data2',
            'request3': 'data3',
            'request4': 'data4',
        }
        self.iterator = iter(self.data)

    def return_data(self, request_id):
        return self.data.get(request_id)


@pytest.fixture(name='mock_handover')
def _mock_handover(mockserver):
    mocker = LogisticPlatformRequestGetMocker()

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/internal/documents/request/get_handover',  # noqa E501
    )
    def mock_get_handover(request):
        assert request.query['request_ids']
        is_editable = request.query.get('editable_format')
        request_ids = request.query['request_ids'].split(',')
        fulldata = str()
        for request_id in request_ids:
            data = mocker.return_data(request_id)
            fulldata += data
            if data is None:
                return mockserver.make_response(
                    status=404, json={'error': 'not find'},
                )
        return mockserver.make_response(
            response=fulldata,
            content_type='octet/stream' if is_editable else 'application/pdf',
        )

    return mock_get_handover


async def test_getting_handover_stq(
        stq_runner, mock_handover, get_notification,
):
    stq_params = dict(COMON_STQ_PARAMS)
    stq_params['request_ids'] = 'request1,request2,request3,request4'
    await stq_runner.logistic_platform_documents_generate_handover.call(  # noqa E501
        task_id='id', kwargs=stq_params,
    )
    assert get_notification.times_called == 1
    assert mock_handover.times_called == 1


async def test_getting_same_handover_stq(
        stq_runner, mock_handover, get_notification,
):
    stq_params = dict(COMON_STQ_PARAMS)
    stq_params['request_ids'] = 'request1,request2,request3,request4'
    await stq_runner.logistic_platform_documents_generate_handover.call(  # noqa E501
        task_id='already_done', kwargs=stq_params,
    )
    assert get_notification.times_called == 1
    assert mock_handover.times_called == 0
