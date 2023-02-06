# pylint: disable=too-many-arguments

import aiohttp.web

_MISSING = object()


def make_order_request(
        city=_MISSING,
        phone=_MISSING,
        source=_MISSING,
        destination=_MISSING,
        due=_MISSING,
        zone_name=_MISSING,
        exclude_fields=(),
        tariff_class=_MISSING,
        interim_destinations=_MISSING,
        offer=_MISSING,
        cost_center=_MISSING,
        cost_centers=_MISSING,
        created_by=_MISSING,
        combo_order=_MISSING,
        cost_centers_id=_MISSING,
        cost_center_values=_MISSING,
        extra_contact_phone=_MISSING,
        requirements=_MISSING,
):
    request = {
        'comment': _make_comment(),
        'phone': _take_not_missing(phone, _make_phone()),
        'source': _take_not_missing(source, make_location()),
        'destination': _take_not_missing(destination, make_location()),
        'class': _make_class(tariff_class),
        'requirements': _make_requirements(requirements),
    }

    if zone_name is _MISSING:
        request['zone_name'] = _make_zone_name()
    elif zone_name is not None:
        request['zone_name'] = zone_name

    if city is _MISSING:
        request['city'] = _make_city()
    elif city is not None:
        request['city'] = city

    if due is not _MISSING:
        request['due'] = due
    for field in exclude_fields:
        request.pop(field)

    if interim_destinations is not _MISSING:
        request['interim_destinations'] = interim_destinations

    if extra_contact_phone is not _MISSING:
        request['extra_contact_phone'] = extra_contact_phone

    if offer is not _MISSING:
        request['offer'] = offer

    if created_by is not _MISSING:
        request['created_by'] = created_by

    # old format (to be removed in years)
    if cost_center is not _MISSING:
        request['cost_center'] = cost_center
    if cost_centers is not _MISSING:
        request['cost_centers'] = cost_centers
    # new format
    if cost_centers_id is not _MISSING:
        request['cost_centers_id'] = cost_centers_id
    if cost_center_values is not _MISSING:
        request['cost_center_values'] = cost_center_values

    if combo_order is not _MISSING:
        request['combo_order'] = combo_order

    return request


def make_location_without(field):
    location = make_location()
    location.pop(field)
    return location


def make_location_with(**kwargs):
    location = make_location()
    for name, value in kwargs.items():
        location[name] = value
    return location


def _take_not_missing(x, y):
    if x is _MISSING:
        return y
    return x


def _make_city():
    return 'Москва'


def _make_zone_name():
    return 'moscow'


def _make_comment():
    return 'some comment'


def _make_cost_center():
    return 'some cost center'


def _make_phone():
    return '+79998887766'


def make_location():
    return {
        'country': 'Россия',
        'fullname': 'Россия, Москва, Новосущевская, 1',
        'geopoint': [33.6, 55.1],
        'locality': 'Москва',
        'porchnumber': '1',
        'premisenumber': '1',
        'thoroughfare': 'Новосущевская',
        'object_type': 'организация',
        'type': 'organization',
    }


def _make_class(tariff_class=_MISSING):
    return 'econom' if tariff_class is _MISSING else tariff_class


def _make_requirements(requirements):
    return {'nosmoking': True} if requirements is _MISSING else requirements


def create_mp_writer(form_data):
    writer = aiohttp.MultipartWriter('form-data')
    for key, value in form_data:
        payload = aiohttp.payload.StringPayload(value)
        payload.set_content_disposition('form-data', name=key)
        writer.append_payload(payload)
    return writer


ORDER_CORP_FIELDS = ('cost_center', 'cost_center_values', 'combo_order')
CHANGE_COST_CENTER_FIELDS = ('cost_center', 'cost_centers')


def check_interim_request(
        cabinet_request,
        external_request,
        cabinet_fields=ORDER_CORP_FIELDS,
        **field_renames,
):
    """Check that request to external fields corresponds to cabinet request

    :param cabinet_request: dict - body sent to cabinet
    :param external_request: dict - body sent to (mocked) external handle
    :param cabinet_fields: iterable - cabinet fields which should correspond
    :param field_renames: kwargs mapping cabinet fields to external fields
    :return: None (or raise AssertionError)
    """
    for cabinet_field in cabinet_fields:
        if cabinet_field in cabinet_request:
            interim_field = field_renames.get(cabinet_field, cabinet_field)
            cabinet_field_value = cabinet_request[cabinet_field]
            external_field_value = external_request[interim_field]
            msg = (
                f'cabinet <{cabinet_field}> ({cabinet_field_value}) must be '
                f'equal to external <{interim_field}> ({external_field_value})'
            )
            assert external_field_value == cabinet_field_value, msg
