# pylint: disable=redefined-outer-name,protected-access
import json

import pytest

from testsuite.utils import ordered_object

from grocery_tasks.crontasks import suggest_update_from_overlord
from grocery_tasks.generated.cron import run_cron


async def test_basic(patch, mockserver, load_json):
    @patch('grocery_tasks.crontasks.suggest_update_from_overlord._yt_upload')
    async def yt_upload(context, dict_entries):
        pass

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/nomenclature-data',
    )
    async def _mock_overlord(request):
        if 'cursor' in request.query:
            return load_json('overlord_empty_response.json')
        return load_json('overlord_basic_response.json')

    await run_cron.main(
        ['grocery_tasks.crontasks.suggest_update_from_overlord', '-t', '0'],
    )

    dict_entries = _jsonize_ids(yt_upload.call['dict_entries'])

    assert dict_entries == [
        {
            'ids': ['id-1'],
            'frequency': 5,
            'name': 'вкусвилл',
            'regional_frequencies': {'111': 5},
        },
        {
            'ids': ['id-2'],
            'frequency': 5,
            'name': 'батончики',
            'regional_frequencies': {'222': 5, '111': 5},
        },
        {
            'ids': ['id-3'],
            'frequency': 5,
            'name': 'мороженое',
            'regional_frequencies': {'111': 5},
        },
        {
            'ids': ['id-4'],
            'frequency': 1,
            'name': 'чудо 2 клубника',
            'regional_frequencies': {'222': 1, '111': 1},
        },
        {
            'ids': ['id-5'],
            'frequency': 1,
            'name': 'oreo молочное с печеньем',
            'regional_frequencies': {'111': 1},
        },
    ]


async def test_same_names(patch, mockserver, load_json):
    @patch('grocery_tasks.crontasks.suggest_update_from_overlord._yt_upload')
    async def yt_upload(context, dict_entries):
        pass

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/nomenclature-data',
    )
    async def _mock_overlord(request):
        if 'cursor' in request.query:
            return load_json('overlord_empty_response.json')
        return load_json('overlord_same_names_response.json')

    await run_cron.main(
        ['grocery_tasks.crontasks.suggest_update_from_overlord', '-t', '0'],
    )

    dict_entries = _jsonize_ids(yt_upload.call['dict_entries'])

    ordered_object.assert_eq(
        dict_entries,
        [
            {
                'ids': ['id-1', 'id-2'],
                'frequency': 5,
                'name': 'батончики',
                'regional_frequencies': {'222': 5, '111': 5},
            },
            {
                'ids': ['id-3'],
                'frequency': 5,
                'name': 'мороженое',
                'regional_frequencies': {'111': 5},
            },
            {
                'ids': ['id-4'],
                'frequency': 1,
                'name': 'чудо 2 клубника',
                'regional_frequencies': {'222': 1, '111': 1},
            },
            {
                'ids': ['id-5', 'id-6'],
                'frequency': 1,
                'name': 'oreo молочное с печеньем',
                'regional_frequencies': {'111': 1, '333': 1},
            },
        ],
        ['ids'],
    )


@pytest.mark.parametrize('string,expected', [('FOO,bar', 'foo bar')])
def test_normalize(string, expected):
    assert suggest_update_from_overlord._normalize(string) == expected


def _jsonize_ids(dict_entries):
    for dict_entry in dict_entries:
        dict_entry['ids'] = json.loads(dict_entry['ids'])

    return dict_entries
