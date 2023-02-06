# pylint: disable=redefined-outer-name
import pytest

from base64 import b64decode


@pytest.fixture(name='mock_feeds_admin')
def mock_feeds_admin(mockserver):
    class Context:
        def __init__(self):
            self.status_code = 200
            self.create_banner_request = None
            self.download_banner_request = None
            self.banner_id = 'banner_id'
            self.campaign_id = ''
            self.image_bin = b''
            self.failed_upload = False

        def set_status_code(self, status_code: int):
            self.status_code = status_code

        def check_download_banner_request(self, media_id: str) -> bool:
            return media_id == self.download_banner_request.query['media_id']

        def set_expected_upload_image_data(
                self, campaign_id: str, image: str, failed: bool = False,
        ):
            ctx.campaign_id = campaign_id
            ctx.image_bin = image
            ctx.failed_upload = failed

        def check_create_banner_request(
                self,
                media_id: str,
                campaign_id: str,
                yandex_uid: str,
                banner_id: int,
                place_id: int,
        ) -> bool:
            expected_request = {
                'service': 'eats-promotions-banner',
                'name': 'direct_banner_id_' + str(banner_id),
                'payload': {
                    'priority': 100,
                    'images': [{'media_id': media_id}],
                    'shortcuts': [],
                    'wide_and_short': [],
                    'advert_settings': {
                        'enabled': True,
                        'direct': {
                            'campaign_id': campaign_id,
                            'yandex_uid': yandex_uid,
                            'banner_id': str(banner_id),
                        },
                    },
                },
                'settings': {
                    'description': 'cpm_banner',
                    'restaurant_ids': [place_id],
                    'recipient_type': 'restaurant',
                },
            }
            for expected_field, field in zip(
                    expected_request, self.create_banner_request.json,
            ):
                if expected_field != field:
                    print('not_expected_result: \n')
                    print(expected_field)
                    print(field)

            return self.create_banner_request.json == expected_request

        @property
        def upload_banner_times_called(self) -> int:
            return upload_banner.times_called

        @property
        def create_banner_times_called(self) -> int:
            return create_banner.times_called

        @property
        def unpublish_banner_times_called(self) -> int:
            return unpublish_banner.times_called

        @property
        def publish_banner_times_called(self) -> int:
            return publish_banner.times_called

        @property
        def download_banner_times_called(self) -> int:
            return download_banner.times_called

    ctx = Context()

    @mockserver.json_handler('/v1/media/upload')
    def upload_banner(request):
        if ctx.failed_upload:
            return mockserver.make_response(
                status=400, json={'code': 400, 'message': 'Error upload'},
            )
        media_id = 'media_id'
        if ctx.campaign_id:
            assert (
                request.get_data().find(
                    bytes('filename="%s"' % ctx.campaign_id, 'utf-8'),
                )
                != -1
            )
            media_id += '_%s' % ctx.campaign_id

        if ctx.image_bin:
            expected_image_bin = b64decode(bytes(ctx.image_bin, 'utf-8'))
            assert request.get_data().find(expected_image_bin) != -1
        return mockserver.make_response(
            status=ctx.status_code,
            json={'media_id': media_id, 'media_type': 'image'},
        )

    @mockserver.json_handler('/feeds-admin/v1/media/download')
    def download_banner(request):
        ctx.download_banner_request = request
        media_id = request.query['media_id']
        image = f'media_object_{media_id}'
        image_binary = image.encode('ascii')
        if ctx.status_code == 200:
            return mockserver.make_response(
                status=200,
                headers={'Content-Type': 'image/png'},
                response=image_binary,
            )
        return mockserver.make_response(status=ctx.status_code)

    @mockserver.json_handler('/feeds-admin/v1/eats-promotions/create')
    def create_banner(request):
        if ctx.status_code == 200:
            ctx.create_banner_request = request
            ctx.banner_id = request.json['payload']['advert_settings'][
                'direct'
            ]['banner_id']
            return mockserver.make_response(
                status=ctx.status_code,
                json={'id': ('direct_banner_id_' + ctx.banner_id)},
            )
        return mockserver.make_response(status=ctx.status_code, json={})

    @mockserver.json_handler('/feeds-admin/v1/eats-promotions/unpublish')
    def unpublish_banner(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/feeds-admin/v1/eats-promotions/publish')
    def publish_banner(request):
        return mockserver.make_response(status=200, json={})

    return ctx
