# pylint: disable=import-error
import asyncio
import datetime

import combo_contractors.fbs.ContractorList as ContractorList
import pytest


NOW = datetime.datetime(2001, 9, 9, 1, 46, 39)


def _fbs_response_extractor(content):
    parsed = ContractorList.ContractorList.GetRootAsContractorList(content, 0)

    contractors = [parsed.List(i) for i in range(parsed.ListLength())]
    contractors = [
        {'dbid_uuid': contractor.DbidUuid().decode()}
        for contractor in contractors
    ]

    return {
        'contractors': contractors,
        'timestamp': datetime.datetime.utcfromtimestamp(parsed.Timestamp()),
    }


async def _perform_requests(taxi_combo_contractors, chunk_count):
    await taxi_combo_contractors.invalidate_caches()
    coros = [
        taxi_combo_contractors.get(
            '/contractors',
            params={'chunk_idx': i, 'chunk_count': chunk_count},
        )
        for i in range(chunk_count)
    ]
    responses = await asyncio.gather(*coros)

    result = []
    for response in responses:
        assert response.status_code == 200
        data = _fbs_response_extractor(response.content)
        result.extend(data['contractors'])

    return result


@pytest.mark.parametrize('chunk_count', [1, 2, 4, 8])
@pytest.mark.pgsql(
    'combo_contractors',
    files=['create_contractor_partitions.sql', 'contractors.sql'],
)
async def test_contractors(
        taxi_combo_contractors, load_json, mocked_time, chunk_count,
):
    mocked_time.set(NOW)

    contractors = await _perform_requests(taxi_combo_contractors, chunk_count)

    assert sorted(contractors, key=lambda x: x['dbid_uuid']) == load_json(
        'contractors.json',
    )
