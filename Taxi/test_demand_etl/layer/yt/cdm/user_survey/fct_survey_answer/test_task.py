import pytest
from demand_etl.layer.yt.cdm.user_survey.fct_survey_answer.wrk.impl import (
    refine_chunk,
    map_answers_stage1,
    map_answers_stage2,
    InputHandbooks,
)

@pytest.mark.parametrize('chunk, expected_result', [
    ['тест', 'тест'],
    [
        'Ситимобил ![](https://avatars.mds.yandex.net/get-pythia/403885/2a0000017bcf6d0bf2f1fcf5e2b41df0001c/orig)',
        'ситимобил'
    ],
    ['Comfort+', 'comfort+'],
    ['Санкт-Петербург', 'санкт-петербург'],
    ['chunk1', 'chunk1'],
    ['chunk!!!11!', 'chunk 11'],
])
def test_refine_chunk(chunk, expected_result):
    assert refine_chunk(chunk) == expected_result


def test_mapper_stage1_empty_handbooks():
    udf = map_answers_stage1([])

    result = udf(
        answer_text=b'',
        option_label_text=b'',
        country_name=b'',
        service_code=b'',
        attribute_processing_required_flg=False
    )
    assert result.filter_out_flg

    result = udf(
        answer_text=b'',
        option_label_text=b'test',
        country_name=b'',
        service_code=b'',
        attribute_processing_required_flg=False
    )
    assert not result.filter_out_flg
    assert not result.translate_flg
    assert result.processed_text == b'test'

    result = udf(
        answer_text=b'answer',
        option_label_text=b'option',
        country_name=b'',
        service_code=b'',
        attribute_processing_required_flg=False
    )
    assert not result.filter_out_flg
    assert not result.translate_flg
    assert result.processed_text == b'option'

    result = udf(
        answer_text=b'answer',
        option_label_text=b'',
        country_name=b'',
        service_code=b'',
        attribute_processing_required_flg=False
    )
    assert not result.filter_out_flg
    assert not result.translate_flg
    assert result.processed_text == b'answer'

    result = udf(
        answer_text=b'answer',
        option_label_text=b'option',
        country_name=b'',
        service_code=b'',
        attribute_processing_required_flg=True
    )
    assert not result.filter_out_flg
    assert not result.filter_out_flg
    assert result.processed_text == b'option'

    result = udf(
        answer_text=b'',
        option_label_text=b'\xe2\x88\xa3\x99',  # not valid utf-8 string
        country_name=b'',
        service_code=b'',
        attribute_processing_required_flg=False
    )
    assert result.filter_out_flg

    result = udf(
        answer_text=b'answer',
        option_label_text=b'',
        country_name=b'',
        service_code=b'',
        attribute_processing_required_flg=False
    )
    assert not result.filter_out_flg
    assert not result.filter_out_flg
    assert result.processed_text == b'answer'


@pytest.fixture
def handbooks():
    return [
        InputHandbooks(
            handbook_name=b'option',
            answer_option_text=b'option-in',
            answer_processed_text=b'option-out',
        ),
        InputHandbooks(
            handbook_name=b'chunk',
            answer_chunk=b'chunk',
            service_code=b'Taxi',
            country_name=b'Russia',
            answer_processed_text=b'result-first',
        ),
        InputHandbooks(
            handbook_name=b'chunk',
            answer_chunk=b'chunk',
            service_code=b'Taxi',
            country_name=b'Russia',
            answer_processed_text=b'result-second',
        ),
        InputHandbooks(
            handbook_name=b'chunk',
            answer_chunk=b'chunk',
            service_code=b'Taxi',
            country_name=b'Russia',
            answer_processed_text=b'result-third',
        ),
        InputHandbooks(
            handbook_name=b'priority',
            answer_processed_text=b'result-first',
            service_code=b'Taxi',
            country_name=b'Russia',
            priority=1,
        ),
        InputHandbooks(
            handbook_name=b'priority',
            answer_processed_text=b'result-second',
            service_code=b'Taxi',
            country_name=b'Russia',
            priority=2,
        ),
        InputHandbooks(
            handbook_name=b'priority',
            answer_processed_text=b'result-none',
            service_code=b'Taxi',
            country_name=b'Russia',
            priority=None,
        ),
    ]


def test_mapper_stage1_filled_handbooks(handbooks):
    udf = map_answers_stage1(handbooks)

    result = udf(
        answer_text=b'',
        option_label_text=b'option-in',
        country_name=b'',
        service_code=b'',
        attribute_processing_required_flg=True
    )
    assert not result.filter_out_flg
    assert result.processed_text == b'option-out'

    result = udf(
        answer_text=b'1112, chunk1 , not-mapped',
        option_label_text=None,
        country_name=b'Russia',
        service_code=b'Taxi',
        attribute_processing_required_flg=True
    )
    assert not result.filter_out_flg
    assert result.processed_text == b'result-first'

    result = udf(
        answer_text=b'!!! , chunk! , not-mapped',
        option_label_text=None,
        country_name=b'Russia',
        service_code=b'Taxi',
        attribute_processing_required_flg=True
    )
    assert not result.filter_out_flg
    assert result.processed_text == b'result-first'


    result = udf(
        answer_text='yandex go,ситимобил'.encode(),
        option_label_text=None,
        country_name=b'Russia',
        service_code=b'Taxi',
        attribute_processing_required_flg=True
    )
    assert not result.filter_out_flg
    assert result.translate_flg
    assert result.translation_text_in == b'yandex go'

    result = udf(
        answer_text=b'yandex go,uber',
        option_label_text=None,
        country_name=b'Russia',
        service_code=b'Taxi',
        attribute_processing_required_flg=False
    )
    assert not result.filter_out_flg
    assert not result.translate_flg
    assert result.processed_text == b'yandex go,uber'

    result = udf(
        answer_text=b'yandex go',
        option_label_text=None,
        country_name=b'Finland',
        service_code=b'Taxi',
        attribute_processing_required_flg=True
    )
    assert not result.filter_out_flg
    assert result.processed_text == b'yandex go'


def test_mapper_stage2_empty_handbooks():
    udf = map_answers_stage2([])

    result = udf(
        translation_text_out=None,
        debug_info=None,
        country_name=None,
        service_code=None,
    )
    assert result.processed_text == b'other'

    result = udf(
        translation_text_out=b'text',
        debug_info=b'',
        country_name=b'',
        service_code=b'',
    )
    assert result.processed_text == b'other'


def test_mapper_stage2_filled_handbooks(handbooks):
    udf = map_answers_stage2(handbooks)

    result = udf(
        translation_text_out=b'chunk',
        debug_info=b'',
        country_name=b'Russia',
        service_code=b'Taxi',
    )
    assert result.processed_text == b'result-first'

    result = udf(
        translation_text_out=b'chunklong',
        debug_info=b'',
        country_name=b'Russia',
        service_code=b'Taxi',
    )
    assert result.processed_text == b'result-first'

    result = udf(
        translation_text_out=b'chunk',
        debug_info=b'',
        country_name=b'Finland',
        service_code=b'Taxi',
    )
    assert result.processed_text == b'other'

    result = udf(
        translation_text_out=b'wrong',
        debug_info=b'',
        country_name=b'Russia',
        service_code=b'Taxi',
    )
    assert result.processed_text == b'other'
