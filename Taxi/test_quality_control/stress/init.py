import asyncio

from taxi.util import client_session
from taxi.util import itertools_ext


BATCH_COUNT = 1000
MAX_COUNT = int(1e6)
CITY = 'Москва'


async def prepare(host):
    entity_type = 'driver'
    entity_ids = list(range(MAX_COUNT))
    await prepare_data(host, entity_type, entity_ids)


def get_session():
    return client_session.get_client_session(
        headers={
            'Host': 'quality-control.taxi.tst.yandex.net',
            'YaTaxi-Api-Key': 'qc-stress',
        },
    )


async def prepare_data(host, entity_type, entity_ids):
    async with get_session() as session:
        for batch, items in enumerate(
                itertools_ext.chunks(entity_ids, BATCH_COUNT),
        ):

            async def post():
                response_data = await session.post(
                    url='{host}/api/v1/data?type={type}'.format(
                        host=host, type=entity_type,
                    ),
                    json=[
                        {
                            'id': str(x),
                            'type': entity_type,
                            'data': {'city': CITY, 'park_id': str(batch + 1)},
                        }
                        for x in items
                    ],
                )
                if response_data.status != 200:
                    return response_data

                return await session.post(
                    url=(
                        '{host}/api/v1/state?type={type}&exam={exam_code}'
                        ''.format(
                            host=host, type=entity_type, exam_code='dkvu',
                        )
                    ),
                    json=[
                        {
                            'id': str(x),
                            'present': {
                                'can_pass': True,
                                'sanctions': ['orders_off'],
                            },
                        }
                        for x in items
                    ],
                )

            text = ''
            status = None
            for _ in range(5):
                response = await post()
                status = response.status
                if status == 200:
                    break

                text = await response.text()
                await asyncio.sleep(2)

            if status != 200:
                raise Exception(text)
