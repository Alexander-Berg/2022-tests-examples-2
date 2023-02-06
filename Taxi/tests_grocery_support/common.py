import json
import uuid

from . import models


def create_default_customer(pgsql, now, personal_phone_id='p_phone_id'):
    return models.Customer(
        pgsql,
        personal_phone_id=personal_phone_id,
        comments=[
            {
                'comment': 'Unicorn, be aware of a horn',
                'support_login': 'superSupport',
                'timestamp': now.isoformat(),
            },
        ],
        phone_id='phone_id',
        yandex_uid='838101',
        antifraud_score='good',
    )


def create_system_customer(pgsql, now):
    return models.Customer(
        pgsql,
        personal_phone_id='personal_phone_id',
        comments=[
            {
                'comment': 'Unicorn, be aware of a horn',
                'support_login': 'system_yandex_login',
                'timestamp': now.isoformat(),
            },
        ],
        phone_id='phone_id',
        yandex_uid='838101',
        antifraud_score='good',
    )


def create_ml_customer(pgsql, now):
    return models.Customer(
        pgsql,
        personal_phone_id='personal_phone_id',
        comments=[
            {
                'comment': 'Unicorn, be aware of a horn',
                'support_login': 'ML_login',
                'timestamp': now.isoformat(),
            },
        ],
        phone_id='phone_id',
        yandex_uid='838101',
        antifraud_score='good',
    )


def create_situation(pgsql, maas_id, compensation_id=None):
    return models.Situation(
        pgsql,
        bound_compensation=compensation_id,
        source='call',
        products=['id1', 'id2'],
        comment='Oh no! Anyway...',
        has_photo=True,
        situation_id=str(uuid.uuid4()),
        maas_id=maas_id,
        order_id='order_id',
    )


def create_situation_v2(
        pgsql,
        maas_id,
        compensation_id=None,
        situation_uuid=None,
        situation_code='some_code',
):
    sit_id = str(uuid.uuid4()) if situation_uuid is None else situation_uuid
    return models.SituationV2(
        pgsql,
        bound_compensation=compensation_id,
        source='call',
        product_infos=[
            {
                'product_id': 'id1:st-md',
                'item_price': '8',
                'quantity': 1,
                'currency': 'RUB',
            },
        ],
        comment='Oh no! Anyway...',
        has_photo=True,
        situation_id=sit_id,
        maas_id=maas_id,
        order_id='order_id',
        situation_code=situation_code,
    )


def create_compensation(pgsql, comp_id, maas_id, user, situations=None):
    return models.Compensation(
        pgsql,
        maas_id=maas_id,
        compensation_id=comp_id,
        order_id='order_id',
        support_login=user.comments[0]['support_login'],
        personal_phone_id=user.personal_phone_id,
        rate=15,
        compensation_type='promocode',
        is_full_refund=False,
        promocode='ASDFGHPROMO',
        situation_ids=situations,
    )


def create_compensation_v2(
        pgsql,
        comp_id,
        maas_id,
        user,
        situations=None,
        main_situation_id=None,
        compensation_info=None,
        source=None,
        order_id='order_id',
        rate=15,
        cancel_reason=None,
        compensation_type='promocode',
        is_full=False,
        is_promised=False,
        error_code=None,
        main_situation_code=None,
        created=models.NOW_DT,
):
    if compensation_info is None:
        compensation_info = get_promocode_info(rate)

    return models.CompensationV2(
        pgsql,
        maas_id=maas_id,
        compensation_id=comp_id,
        order_id=order_id,
        support_login=user.comments[0]['support_login'],
        personal_phone_id=user.personal_phone_id,
        rate=rate,
        compensation_type=compensation_type,
        situation_ids=situations,
        main_situation_id=main_situation_id,
        raw_compensation_info=json.dumps(compensation_info),
        cancel_reason=cancel_reason,
        source=source,
        is_full_refund=is_full,
        is_promised=is_promised,
        error_code=error_code,
        main_situation_code=main_situation_code,
        created=created,
    )


def get_promocode_info(compensation_value=15):
    return {
        'generated_promo': 'QWERTY',
        'compensation_value': compensation_value,
        'status': 'success',
    }


def create_matrix_response_json(situation):
    return {
        'compensation_packs': [],
        'situation_id': situation.maas_id,
        'situation_code': 'some_code',
        'situation_title': 'situation_title',
        'situation_group_title': 'situation_group_title',
    }


def create_filtering_response_json(situation):
    return {
        'compensation_packs': [
            {
                'compensations': [
                    {
                        'id': 123,
                        'description': 'tips',
                        'is_full_refund': False,
                        'type': 'tipsRefund',
                        'notification': '',
                    },
                ],
                'id': 1,
            },
            {
                'compensations': [
                    {
                        'id': 124,
                        'description': 'delivery',
                        'is_full_refund': False,
                        'type': 'deliveryRefund',
                        'notification': '',
                    },
                ],
                'id': 2,
            },
        ],
        'situation_id': situation.maas_id,
        'situation_code': 'some_code',
        'situation_title': 'situation_title',
        'situation_group_title': 'situation_group_title',
    }


def create_tristero_response_json(situation):
    return {
        'compensation_packs': [
            {
                'compensations': [
                    {
                        'id': 123,
                        'description': 'refund',
                        'is_full_refund': False,
                        'type': 'refund',
                        'notification': '',
                    },
                ],
                'id': 1,
            },
            {
                'compensations': [
                    {
                        'id': 124,
                        'description': 'voucher',
                        'is_full_refund': False,
                        'type': 'voucher',
                        'notification': '',
                    },
                ],
                'id': 2,
            },
            {
                'compensations': [
                    {
                        'id': 125,
                        'description': 'promocode',
                        'is_full_refund': False,
                        'type': 'promocode',
                        'notification': '',
                        'rate': 10,
                    },
                ],
                'id': 3,
            },
        ],
        'situation_id': situation.maas_id,
        'situation_code': 'some_code',
        'situation_title': 'situation_title',
        'situation_group_title': 'situation_group_title',
    }


def get_submit_situation_response(
        situation, compensation, code, eats_type=None,
):
    if not eats_type:
        eats_type = compensation.compensation_type
    return {
        'compensation_packs': [
            {
                'compensations': [
                    {
                        'id': compensation.maas_id,
                        'description': compensation.description,
                        'is_full_refund': compensation.is_full_refund,
                        'max_value': compensation.max_value,
                        'min_value': compensation.min_value,
                        'notification': '',
                        'rate': compensation.rate,
                        'type': eats_type,
                    },
                ],
                'id': 123,
            },
        ],
        'situation_id': situation.maas_id,
        'situation_code': code,
        'situation_title': 'situation_title',
        'situation_group_title': 'situation_group_title',
    }


def get_eats_compensation_pack(pack_id, compensation):
    return {
        'pack': {
            'id': pack_id,
            'compensations': [
                {
                    'id': compensation.maas_id,
                    'description': compensation.description,
                    'type': compensation.compensation_type,
                    'rate': compensation.rate,
                    'is_full_refund': compensation.is_full_refund,
                    'max_value': compensation.max_value,
                    'min_value': compensation.min_value,
                    'notification': '',
                },
            ],
        },
    }


def get_situation_by_code_response(situation, code):
    return {
        'situation': {
            'group': {
                'description': '',
                'id': 1,
                'priority': 1,
                'title': 'test_group',
            },
            'code': code,
            'id': situation.maas_id,
            'extra_parameters': [],
            'title': 'test_situation',
            'violation_level': '',
            'responsible': '',
            'priority': 1,
            'is_system': False,
            'is_need_confirmation': False,
            'is_available_before_final_status': True,
        },
        'situation_group_title': '',
        'matrix_id': 1,
        'matrix_code': '123',
    }
