# pylint: disable=unused-variable
import pytest

CONFIG = {
    'order.cancel.reaction.client_charge': {
        'label': 'order.cancel.reaction.client_charge',
        'payload_schema': {},
    },
    'order.cancel.reaction.compensation': {
        'label': 'order.cancel.reaction.compensation',
        'payload_schema': {
            'limit': {
                'label': 'order.cancel.reaction.compensation.limit',
                'type': 'float',
            },
            'limit_currency': {
                'label': 'order.cancel.reaction.compensation.limit_currency',
                'type': 'enum',
                'values': ['RUB', 'BYN', 'KZT'],
            },
            'rate': {
                'label': 'order.cancel.reaction.compensation.rate',
                'type': 'integer',
            },
        },
    },
    'order.cancel.reaction.notification': {
        'label': 'order.cancel.reaction.notification',
        'payload_schema': {
            'code': {
                'label': 'order.cancel.reaction.notification.code',
                'type': 'string',
            },
        },
    },
    'order.cancel.reaction.restoration_reimbursement': {
        'label': 'order.cancel.reaction.restoration_reimbursement',
        'payload_schema': {},
    },
    'order.cancel.reaction.return_promocode': {
        'label': 'order.cancel.reaction.return_promocode',
        'payload_schema': {},
    },
    'order.cancel.reaction.unblock': {
        'label': 'order.cancel.reaction.unblock',
        'payload_schema': {},
    },
}

EXPECTED_DATA = {
    'order.cancel.reaction.client_charge': {
        'label': 'Снятие средств',
        'payload_schema': {},
    },
    'order.cancel.reaction.compensation': {
        'label': 'Промокод',
        'payload_schema': {
            'limit': {'label': 'Лимит на размер скидки', 'type': 'float'},
            'limit_currency': {
                'label': 'Валюта лимита',
                'type': 'enum',
                'values': ['RUB', 'BYN', 'KZT'],
            },
            'rate': {
                'label': 'Процент скидки по промокоду',
                'type': 'integer',
            },
        },
    },
    'order.cancel.reaction.notification': {
        'label': 'Уведомление',
        'payload_schema': {
            'code': {'label': 'Код уведомления', 'type': 'string'},
        },
    },
    'order.cancel.reaction.restoration_reimbursement': {
        'label': 'Компенсация ресторану',
        'payload_schema': {},
    },
    'order.cancel.reaction.return_promocode': {
        'label': 'Возврат промокода',
        'payload_schema': {},
    },
    'order.cancel.reaction.unblock': {
        'label': 'Разблокировка средств',
        'payload_schema': {},
    },
}


@pytest.mark.config(EATS_COMPENSATIONS_MATRIX_REACTION_PAYLOAD_SCHEMAS=CONFIG)
async def test_reaction_payload_schemas(taxi_eats_compensations_matrix):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/cancel/reaction/payload-schemas/',
    )
    assert response.status_code == 200
    assert response.json() == EXPECTED_DATA
