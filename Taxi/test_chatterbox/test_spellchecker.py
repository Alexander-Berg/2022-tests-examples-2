import csv
import io
import json

import pytest

from chatterbox.api import spellchecker


@pytest.mark.parametrize(
    'dictionary_ids, text, expected_response',
    [
        [
            ['common', 'eats', 'taxi'],
            'текст ошибка для проверки',
            {
                'errors': [
                    {
                        'position': 6,
                        'text': 'ошибка',
                        'variants': [
                            {
                                'text': 'правильный вариант 2',
                                'dictionaries': ['eats', 'taxi'],
                            },
                            {
                                'text': 'правильный вариант 1',
                                'dictionaries': ['common'],
                            },
                        ],
                    },
                ],
            },
        ],
        [
            ['taxi'],
            'яндекс.такси ЯНДЕКС.ТАКСИ Яндекс.Такси',
            {
                'errors': [
                    {
                        'position': 0,
                        'text': 'яндекс.такси',
                        'variants': [
                            {'text': 'Яндекс.Такси', 'dictionaries': ['taxi']},
                        ],
                    },
                    {
                        'position': 13,
                        'text': 'ЯНДЕКС.ТАКСИ',
                        'variants': [
                            {'text': 'Яндекс.Такси', 'dictionaries': ['taxi']},
                        ],
                    },
                ],
            },
        ],
        [
            ['belarus', 'bzhik'],
            'вот Белоруссия не гусь, не бжик, не пшик',
            {
                'errors': [
                    {
                        'position': 4,
                        'text': 'Белоруссия',
                        'variants': [
                            {'text': 'Беларусь', 'dictionaries': ['belarus']},
                        ],
                    },
                    {
                        'position': 18,
                        'text': 'гусь',
                        'variants': [
                            {
                                'text': 'кусь',
                                'dictionaries': ['belarus', 'bzhik'],
                            },
                        ],
                    },
                    {
                        'position': 27,
                        'text': 'бжик',
                        'variants': [
                            {'text': 'вжик пыпык', 'dictionaries': ['bzhik']},
                            {'text': 'пшик', 'dictionaries': ['belarus']},
                        ],
                    },
                ],
            },
        ],
        [
            ['common'],
            'не .в. коем   случае',
            {
                'errors': [
                    {
                        'position': 0,
                        'text': 'не .в. коем   случае',
                        'variants': [
                            {
                                'text': 'ни в коем случае',
                                'dictionaries': ['common'],
                            },
                        ],
                    },
                ],
            },
        ],
    ],
)
async def test_spellchecker(
        load, cbox, dictionary_ids, text, expected_response,
):
    max_words = cbox.app.config.CHATTERBOX_SPELLCHECKER_WORDS_LIMIT
    dictionaries = json.loads(load('spellchecker_dictionaries.json'))
    for dictionary_id in dictionary_ids:
        data = dictionaries[dictionary_id].items()
        with io.StringIO() as filelike:
            csv_writer = csv.writer(filelike, delimiter=';')
            csv_writer.writerow(spellchecker.REQUIRED_FIELDNAMES)
            for row in dictionaries[dictionary_id].items():
                csv_writer.writerow(row)
            csv_data = filelike.getvalue()
        await cbox.post(
            '/v1/spellchecker/dictionary/',
            raw_data=csv_data,
            params={'dictionary_id': dictionary_id},
            headers={
                'Content-Type': 'application/octet-stream',
                'X-File-Name': f'{dictionary_id}.csv',
            },
        )
        if any(
                any(len(item.split()) > max_words for item in row)
                for row in data
        ):
            assert cbox.status == 400
            continue
        assert cbox.status == 200
        await cbox.query(
            '/v1/spellchecker/dictionary/',
            params={'dictionary_id': dictionary_id},
        )
        assert cbox.status == 200
        assert cbox.body == csv_data
    spellchecker_query_data = {'text': text, 'dictionaries': dictionary_ids}
    await cbox.post('/v1/spellchecker/', data=spellchecker_query_data)
    assert cbox.status == 200
    assert cbox.body_data == expected_response


def _csv_dump(headers, data):
    with io.StringIO() as filelike:
        csv_writer = csv.writer(filelike, delimiter=';')
        csv_writer.writerow(headers)
        for row in data:
            csv_writer.writerow(row)
        return filelike.getvalue()
