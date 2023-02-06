import pytest

from test_quality_control import utils as test_utils


async def test_lb_writer_passes_a():
    pass


async def test_lb_writer_passes_b():
    pass


@pytest.mark.config(
    QC_LOGBROKER_EVENT_PRODUCING={
        'enabled': True,
        'fallback_strategy': 'None',
    },
)
async def test_lb_writer_state_save_exam_state(qc_client, mock_lb_producer):
    mock_lb_producer.add_expected_seq_no([1, 1, 2, 3])
    mock_lb_producer.add_expected_data(
        [
            b'{"source": "_save_exam_state", "pass_id": "61ca68e00523c34c5f6'
            b'18f59", "modified_ts": "Timestamp(0, 0)", "timestamp": "2021-1'
            b'2-28T01:31:12", "entity_type": "driver", "entity_id": "1", "ex'
            b'am_code": "dkk", "enabled": false, "reason": null, "identity":'
            b' null, "sanctions": ["orders_off"]}',
            b'{"source": "_save_exam_state", "pass_id": "61ca68e00523c34c5f6'
            b'18f5a", "modified_ts": "Timestamp(0, 0)", "timestamp": "2021-1'
            b'2-28T01:31:12", "entity_type": "driver", "entity_id": "2", "ex'
            b'am_code": "dkk", "enabled": false, "reason": null, "identity":'
            b' null, "sanctions": ["orders_off"]}',
            b'{"source": "_save_exam_state", "pass_id": "61ca68e00523c34c5f6'
            b'18f59", "modified_ts": "None", "timestamp": "2021-12-28T01:31:'
            b'12", "entity_type": "driver", "entity_id": "1", "exam_code": "'
            b'dkk", "enabled": true, "reason": null, "identity": null, "sanc'
            b'tions": null}',
            b'{"source": "_save_exam_state", "pass_id": "61ca68e00523c34c5f6'
            b'18f5a", "modified_ts": "None", "timestamp": "2021-12-28T01:31:'
            b'12", "entity_type": "driver", "entity_id": "2", "exam_code": "'
            b'dkk", "enabled": true, "reason": null, "identity": null, "sanc'
            b'tions": null}',
        ],
    )

    entity_jack = {'id': '1', 'type': 'driver'}
    entity_alice = {'id': '2', 'type': 'driver'}
    await test_utils.prepare_entity(
        qc_client, entity_jack['type'], entity_jack['id'],
    )
    await test_utils.prepare_entity(
        qc_client, entity_alice['type'], entity_alice['id'],
    )

    exam_code = 'dkk'
    # вызываем на ДКК
    await test_utils.prepare_exam(
        qc_client,
        entity_jack['type'],
        entity_jack['id'],
        exam_code,
        test_utils.STATES.CALL,
    )
    await test_utils.prepare_exam(
        qc_client,
        entity_alice['type'],
        entity_alice['id'],
        exam_code,
        test_utils.STATES.CALL,
    )

    # выключаем ДКК
    await test_utils.prepare_exam(
        qc_client,
        entity_jack['type'],
        entity_jack['id'],
        exam_code,
        test_utils.STATES.DISABLE,
    )
    await test_utils.prepare_exam(
        qc_client,
        entity_alice['type'],
        entity_alice['id'],
        exam_code,
        test_utils.STATES.DISABLE,
    )

    mock_lb_producer.check_seq_no()
    mock_lb_producer.check_data()


async def test_lb_writer_state_b():
    pass


async def test_lb_writer_state_c():
    pass


async def test_lb_writer_state_d():
    pass
