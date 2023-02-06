STQ_PARAMS = {'employer_code': 'some_employer'}


class LogisticPlatformRequestGetMocker:
    def __init__(self) -> None:
        self.data = [
            {
                'report_string': (
                    'header1;header2;header3\nval1;val2;val3\nval1;val2;val3'
                ),
                'cursor': 'cursor1',
            },
            {'report_string': 'val1;val2;val3'},
        ]
        self.cursors = [None, 'cursor1']
        self.iterator = iter(self.data)
        self.cursor_iterator = iter(self.cursors)

    def return_data(self, cursor):
        try:
            assert cursor == next(self.cursor_iterator)
            return next(self.iterator)
        except StopIteration:
            return {}


async def test_getting_report_stq(stq_runner, mockserver, get_notification):

    request_get_mocker = LogisticPlatformRequestGetMocker()

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/internal/documents/request/get_report',  # noqa E501
    )
    def get_report(request):
        return request_get_mocker.return_data(request.query.get('cursor'))

    await stq_runner.logistic_platform_documents_generate_report.call(  # noqa E501
        task_id='id', kwargs=STQ_PARAMS,
    )
    assert get_notification.times_called == 1
    assert get_report.times_called == 2


async def test_getting_same_report_stq(
        stq_runner, mockserver, get_notification,
):
    request_get_mocker = LogisticPlatformRequestGetMocker()

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/internal/documents/request/get_report',  # noqa E501
    )
    def get_report(request):
        return request_get_mocker.return_data(request.query.get('cursor'))

    await stq_runner.logistic_platform_documents_generate_report.call(  # noqa E501
        task_id='already_done', kwargs=STQ_PARAMS,
    )
    assert get_notification.times_called == 1
    assert get_report.times_called == 0
