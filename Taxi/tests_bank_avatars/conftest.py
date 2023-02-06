import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401
from bank_avatars_plugins import *  # noqa: F403 F401


@pytest.fixture
def avatars_mds_mock(mockserver):
    def make_response(image_name, group_id):
        return {
            'imagename': image_name,
            'group-id': group_id,
            'meta': {'orig-format': 'JPEG'},
            'sizes': {
                'orig': {
                    'height': 640,
                    'path': f'/get-fintech/{group_id}/{image_name}/orig',
                    'width': 1024,
                },
                'sizename': {
                    'height': 200,
                    'path': f'/get-fintech/{group_id}/{image_name}/sizename',
                    'width': 200,
                },
            },
        }

    class Context:
        def __init__(self):
            self.image_name = None
            self.group_id = None

            self.put_unnamed_handler = None
            self.put_named_handler = None

        def set_image_name(self, image_name):
            self.image_name = image_name

        def set_group_id(self, group_id):
            self.group_id = group_id

    context = Context()

    @mockserver.json_handler(
        r'/avatars-mds/put-fintech/(?P<image_name>\w+)', regex=True,
    )
    def _mock_put_named_handler(request, image_name):
        return make_response(image_name, context.group_id)

    @mockserver.json_handler('/avatars-mds/put-fintech', prefix=True)
    def _mock_put_unnamed_handler(request):
        return make_response(context.image_name, context.group_id)

    context.put_unnamed_handler = _mock_put_unnamed_handler
    context.put_named_handler = _mock_put_named_handler

    return context
