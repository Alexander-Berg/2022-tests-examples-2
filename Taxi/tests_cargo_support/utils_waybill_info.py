def create_point_execution(
        point_type,
        visit_status,
        point_id,
        claim_point_id,
        *,
        segment_id,
        visit_order,
        is_resolved,
        is_return_required,
        last_status_change_ts,
):
    point_execution = {
        'segment_id': segment_id,
        'point_id': point_id,
        'claim_point_id': claim_point_id,
        'type': point_type,
        'is_resolved': is_resolved,
        'last_status_change_ts': last_status_change_ts,
        'visit_status': visit_status,
        'changelog': [],
        'visit_order': visit_order,
        'label': point_id,
        'phones': [],
        'address': {},
        'need_confirmation': False,
        'location': {'id': 'location_id_1', 'coordinates': [50, 50]},
    }

    if is_return_required is not None:
        point_execution['is_return_required'] = is_return_required

    return point_execution


def add_point_execution(
        waybill_info,
        point_type,
        visit_status,
        point_id,
        claim_point_id,
        *,
        segment_id='segment_id_1',
        visit_order=1,
        is_resolved=False,
        is_return_required=None,
        last_status_change_ts='2020-01-01T10:00:00+00:00',
):
    point_execution = create_point_execution(
        point_type,
        visit_status,
        point_id,
        claim_point_id,
        segment_id=segment_id,
        visit_order=visit_order,
        is_resolved=is_resolved,
        is_return_required=is_return_required,
        last_status_change_ts=last_status_change_ts,
    )

    if 'points' not in waybill_info['execution']:
        waybill_info['execution']['points'] = []

    waybill_info['execution']['points'].append(point_execution)


def create_wb_segment_info(
        segment_id,
        *,
        claim_id,
        corp_client_id,
        yandex_uid,
        due,
        is_skipped,
        custom_context,
):
    segment_info = {
        'id': segment_id,
        'status': 'pickuped',
        'updated_ts': '2020-01-01T10:00:00+00:00',
        'zone_id': 'zone_id_1',
        'client_info': {'payment_info': {'type': 'cash'}},
        'claim_id': claim_id,
    }

    if corp_client_id is not None:
        segment_info['corp_client_id'] = corp_client_id
    if yandex_uid is not None:
        segment_info['yandex_uid'] = yandex_uid
    if due is not None:
        segment_info['due'] = due
    if is_skipped is not None:
        segment_info['is_skipped'] = is_skipped
    if custom_context is not None:
        segment_info['custom_context'] = custom_context

    return segment_info


def add_wb_segment_info(
        waybill_info,
        segment_id,
        *,
        claim_id='claim_id_1',
        corp_client_id='corp_client_id_1',
        yandex_uid=None,
        due=None,
        is_skipped=None,
        custom_context=None,
):
    segment_info = create_wb_segment_info(
        segment_id,
        claim_id=claim_id,
        corp_client_id=corp_client_id,
        yandex_uid=yandex_uid,
        due=due,
        is_skipped=is_skipped,
        custom_context=custom_context,
    )

    if 'segments' not in waybill_info['execution']:
        waybill_info['execution']['segments'] = []

    waybill_info['execution']['segments'].append(segment_info)


def create_claim_segment(
        segment_id,
        *,
        allow_batch,
        allow_alive_batch_v1,
        allow_alive_batch_v2,
        zone_id,
        employer,
        custom_context,
        dynamic_context,
        corp_client_id,
):
    claim_segment = {
        'id': segment_id,
        'items': [],
        'locations': [],
        'points': [],
        'performer_requirements': {
            'taxi_classes': [],
            'special_requirements': {'virtual_tariffs': []},
        },
        'allow_batch': allow_batch,
        'allow_alive_batch_v1': allow_alive_batch_v1,
        'allow_alive_batch_v2': allow_alive_batch_v2,
        'client_info': {'payment_info': {'type': 'cash'}},
        'zone_id': zone_id,
    }

    if employer is not None:
        claim_segment['employer'] = employer
    if custom_context is not None:
        claim_segment['custom_context'] = custom_context
    if dynamic_context is not None:
        claim_segment['dynamic_context'] = dynamic_context
    if corp_client_id is not None:
        claim_segment['corp_client_id'] = corp_client_id

    return claim_segment


def add_claim_segment(
        waybill_info,
        segment_id,
        *,
        allow_batch=True,
        allow_alive_batch_v1=True,
        allow_alive_batch_v2=True,
        zone_id='zone_id_1',
        employer='employer_1',
        custom_context=None,
        dynamic_context=None,
        corp_client_id='corp_client_id_1',
):
    claim_segment = create_claim_segment(
        segment_id,
        allow_batch=allow_batch,
        allow_alive_batch_v1=allow_alive_batch_v1,
        allow_alive_batch_v2=allow_alive_batch_v2,
        zone_id=zone_id,
        employer=employer,
        custom_context=custom_context,
        dynamic_context=dynamic_context,
        corp_client_id=corp_client_id,
    )

    if 'segments' not in waybill_info:
        waybill_info['segments'] = []

    waybill_info['segments'].append(claim_segment)


def set_taxi_order_info(
        waybill_info,
        *,
        taxi_order_id='taxi_order_id_1',
        park_id='park_id_1',
        driver_id='driver_id_1',
        name='Name',
        car_id='car_id_1',
        car_number='car_number_1',
        car_model='car_model_1',
        tariff_class=None,
        phone_pd_id=None,
        transport_type=None,
):
    waybill_info['execution']['taxi_order_info'] = {
        'order_id': taxi_order_id,
        'performer_info': {
            'name': name,
            'park_id': park_id,
            'driver_id': driver_id,
            'car_id': car_id,
            'car_number': car_number,
            'car_model': car_model,
        },
    }

    if tariff_class is not None:
        waybill_info['execution']['taxi_order_info'][
            'tariff_class'
        ] = tariff_class
    if phone_pd_id is not None:
        waybill_info['execution']['taxi_order_info'][
            'phone_pd_id'
        ] = phone_pd_id
    if transport_type is not None:
        waybill_info['execution']['taxi_order_info'][
            'transport_type'
        ] = transport_type


def set_cargo_order_info(
        waybill_info,
        *,
        cargo_order_id='11111111-1111-1111-1111-111111111111',
        provider_order_id='provider_order_id_1',
):
    waybill_info['execution']['cargo_order_info'] = {
        'order_id': cargo_order_id,
        'provider_order_id': provider_order_id,
        'use_cargo_pricing': True,
        'order_cancel_performer_reason_list': [],
    }
