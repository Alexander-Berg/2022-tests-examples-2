import copy

import pytest

from tests_ivr_dispatcher import fwt_utils as utils

CALLS_EVENTS_HISTORY_URL = '/v1/ivr-framework/get-calls-events-history'


@pytest.mark.config(
    IVR_FRAMEWORK_FLOW_CONFIG={
        'eda_support_flow_couriers': {
            'asr_config': utils.ASR_CONFIG,
            'local_vad_config': utils.LOCAL_VAD_CONFIG,
            'tts_config': utils.TTS_CONFIG,
        },
        'market_support_flow': {
            'asr_config': utils.ASR_CONFIG,
            'local_vad_config': utils.LOCAL_VAD_CONFIG,
            'tts_config': utils.TTS_CONFIG,
        },
        'taxi_cc_sf_flow': {
            'asr_config': utils.ASR_CONFIG,
            'local_vad_config': utils.LOCAL_VAD_CONFIG,
            'tts_config': utils.TTS_CONFIG,
        },
        'taxi_disp_queue_emulation_flow': {
            'asr_config': utils.ASR_CONFIG,
            'local_vad_config': utils.LOCAL_VAD_CONFIG,
            'tts_config': utils.TTS_CONFIG,
        },
    },
)
@pytest.mark.pgsql('ivr_api', files=['fill_worker_actions.sql'])
@pytest.mark.parametrize(
    [
        'session_id',
        'call_id',
        'client_context',
        'cursor',
        'limit',
        'expected_status',
        'expected_data',
    ],
    [
        pytest.param(
            '8323635c8bcb4bfca6752c1daffde5c2',
            'c43f3c46-77d7-4faf-ab86-7464c30d686f',
            {'test1': 'test', 'test2': True, 'test3': 8200},
            0,
            8,
            200,
            'expected_data_1.json',
            id='originate',
        ),
        pytest.param(
            '8029d12c-22e1-4cda-af78-868b8f72df34',
            '38eee5a0-5d02-4291-8d6b-6b9762040eb1',
            {
                'application': 'call_center',
                'disp_number': '890000',
                'ask_attempts': 2,
                'ask_wav_path': 'taxi_disp_queue_emulation_flow.ask_clean',
                'moh_wav_path': None,
                'sms_text_path': 'luring_app.sms_text.link',
                'queue_wait_time': 1,
                'should_send_sms': False,
                'notify_sms_wav_path': (
                    'taxi_disp_luring_flow.notify_sms_sending_link_human_voice'
                ),
                'should_play_pre_hangup': True,
                'bad_user_input_wav_path': (
                    'taxi_disp_queue_emulation_flow.bad_user_input'
                ),
                'invalid_input_wait_time': 1,
                'should_switch_to_operator': True,
                'should_play_operators_busy': False,
                'taxi_disp_luring_wait_time': 5000,
            },
            8,
            6,
            200,
            'expected_data_2.json',
            id='answer playback error',
        ),
        pytest.param(
            '56208b3f-8d8d-4e8d-8406-f14ae4a72be3',
            '557ac7ee-fa3b-11ec-a393-5742a97837ba',
            {
                'initial_timepoint': '2022-06-15T10:55:31.193134+0000',
                'performing_action': 5,
            },
            14,
            8,
            200,
            'expected_data_3.json',
            id='answer success',
        ),
        pytest.param(
            'a48c0f08-72c7-4cc8-9bb0-25ea51003d9c',
            'bdf5bc12-830c-4934-af97-0db71050aa6b',
            {'performing_action': 4},
            22,
            8,
            200,
            'expected_data_4.json',
            id='answer ask hangup',
        ),
    ],
)
async def test_calls_events_history(
        taxi_ivr_dispatcher,
        load_json,
        mongodb,
        mock_personal,
        session_id,
        call_id,
        client_context,
        cursor,
        limit,
        expected_status,
        expected_data,
):
    context = copy.deepcopy(utils.NEW_CONTEXT)
    context['_id'] = session_id
    context['context']['call_id'] = call_id
    context['context']['client_context'] = client_context
    mongodb.ivr_disp_sessions.insert_one(context)

    params = {'cursor': cursor, 'limit': limit}
    response = await taxi_ivr_dispatcher.get(
        CALLS_EVENTS_HISTORY_URL, params=params,
    )
    assert response.status_code == expected_status
    if expected_data:
        assert response.json() == load_json(expected_data)
