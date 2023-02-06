import pytest

from eats_report_sender.components.senders import base_sender
from eats_report_sender.components.senders import exceptions
from eats_report_sender.generated.service.swagger.models import (
    api as api_module,
)


class DummySender(base_sender.BaseSender):
    async def _send(self, report):
        folder = self.get_mds3_dir_name(report)
        await self.get_files_list_by_dir(folder)


async def test_should_raise_exception_if_empty_dir(
        mockserver, load_json, stq3_context, patch,
):
    @mockserver.handler('/mds-s3', prefix=True)
    async def _mockserver_mds3(request, *args):
        return mockserver.make_response()

    with pytest.raises(exceptions.S3DirectoryIsEmpty):
        await DummySender(stq3_context).send(
            api_module.Report.deserialize(
                load_json('report_data.json')['correct'],
            ),
        )


@pytest.mark.parametrize(
    'report, folder',
    [
        ['with_place_id', 'test_report_type/brand_id/daily/uuid/place_id/'],
        ['without_place_id', 'test_report_type/brand_id/daily/uuid/'],
    ],
)
async def test_base_sender_get_mds3_dir_name(
        mockserver, stq3_context, load_json, report, folder,
):
    @mockserver.handler('/mds-s3', prefix=True)
    async def _mockserver_mds3(request, *args):
        assert request.query['prefix'] == folder
        return mockserver.make_response()

    try:
        assert folder == await DummySender(stq3_context).send(
            api_module.Report.deserialize(
                load_json('report_data.json')[report],
            ),
        )
    except exceptions.S3DirectoryIsEmpty:
        pass
