"""
Script for test /v1/media/upload handle at messenger service
"""
import argparse
import asyncio
import logging

import aiohttp
import os
import urllib.request
import urllib.parse

from taxi import settings as taxi_settings
from taxi import config as taxi_config
from taxi import secdist as taxi_secdist
from taxi.clients import configs
from taxi.clients import tvm as tvm_client

TVM_SERVICE_NAME = 'messenger'

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class Settings(taxi_settings.Settings):
    MESSENGER_BASE_URL = 'http://messenger.taxi.yandex.net'
    if taxi_settings.ENVIRONMENT == taxi_settings.TESTING:
        MESSENGER_BASE_URL = 'http://messenger.taxi.tst.yandex.net'


async def main(
        server: str,
        service: str,
        payload_url: str,
        media_type: str,
        content_type: str,
):
    secdist = taxi_secdist.load_secdist()
    session = aiohttp.ClientSession()
    settings = Settings()
    if server:
        settings.MESSENGER_BASE_URL = server
    configs_client = configs.ConfigsApiClient(session, settings)
    config = taxi_config.Config(configs_client=configs_client)
    await config.refresh_cache()

    tvm = tvm_client.TVMClient(
        service_name=TVM_SERVICE_NAME,
        secdist=secdist,
        config=config,
        session=session,
    )

    tvm2_headers = await tvm.get_auth_headers(TVM_SERVICE_NAME, False)

    media_data = urllib.request.urlopen(payload_url).read()
    url_parts = urllib.parse.urlparse(payload_url)
    file_name = os.path.basename(url_parts.path)

    form = aiohttp.FormData()
    form.add_field(name='content', value=media_data)
    form.add_field(name='media_type', value=media_type)
    form.add_field(name='content_file_name', value=file_name)
    form.add_field(name='service', value=service)
    if content_type:
        form.add_field(name='content_type', value=content_type)

    url = f'{settings.MESSENGER_BASE_URL}/v1/media/upload'

    logger.info('Send upload request, url: %s', url)
    response = await session.request(
        'POST', url, data=form, headers=tvm2_headers,
    )

    if response.status != 200:
        logger.error('Bad response: %s', await response.text())
    else:
        logger.info('Uploaded, response: %s', await response.text())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', type=str, default=None)
    parser.add_argument('--server', type=str, default=None)
    parser.add_argument('--payload_url', type=str, default=None)
    parser.add_argument('--media_type', type=str, default=None)
    parser.add_argument('--content_type', type=str, default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        main(
            args.server,
            args.service,
            args.payload_url,
            args.media_type,
            args.content_type,
        ),
    )
