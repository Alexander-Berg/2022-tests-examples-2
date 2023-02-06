from stall.client.qc_exam import QcExamClient, QcExamRequestError, QcExamError


async def test_common(tap, ext_api):
    with tap.plan(1, 'успешный вызов'):
        # pylint: disable=unused-argument
        async def handle(request):
            return {'code': 'OK'}

        async with await ext_api('qc_exam', handle) as cli:
            cli: QcExamClient

            await cli.call(
                '__entity_id__',
                '__exam__',
                '__caller__',
                '__reqid__',
            )
            tap.passed('qc_exam called without error')


async def test_bad_request(tap, ext_api):
    with tap.plan(1, 'вызов для некорректного курьера'):
        # pylint: disable=unused-argument
        async def handle(request):
            return 400, {
                'code': 'EXAM_IS_NOT_ENABLED',
                'message': '__error_message__',
            }

        async with await ext_api('qc_exam', handle) as cli:
            cli: QcExamClient

            with tap.raises(QcExamRequestError):
                await cli.call(
                    '__entity_id__',
                    '__exam__',
                    '__caller__',
                    '__reqid__',
                )


async def test_fail(tap, ext_api):
    with tap.plan(1, 'сервис упал'):
        # pylint: disable=unused-argument
        async def handle(request):
            return 500, {'code': 'INTERNAL_ERROR'}

        async with await ext_api('qc_exam', handle) as cli:
            cli: QcExamClient

            with tap.raises(QcExamError):
                await cli.call(
                    '__entity_id__',
                    '__exam__',
                    '__caller__',
                    '__reqid__',
                )
