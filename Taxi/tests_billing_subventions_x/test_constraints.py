import json

import pytest
# pylint: disable=too-many-lines

HANDLE = 'v1/rules/match/'


def _get_ids(json_value):
    return {x['id'] for x in json_value['match']}


def get_ids(response):
    return _get_ids(json.loads(response.content))


# datetimes:
# 2020-02-01T00:00:00.000Z 6/Sat 1580515200 <- begin
# 2020-02-01T12:00:00.000Z 6/Sat 1580558400
# 2020-02-10T00:00:00.000Z 1/Mon 1581292800
# 2020-02-11T12:00:00.000Z 2/Tue 1581422400
# 2020-02-12T12:00:00.000Z 3/Wed 1581508800 <- check
# 2020-02-13T12:00:00.000Z 4/Thu 1581595200
# 2020-02-14T12:00:00.000Z 5/Fri 1581681600
# 2020-02-15T12:00:00.000Z 6/Sat 1581768000
# 2020-02-16T12:00:00.000Z 7/Sun 1581854400
# 2020-02-17T12:00:00.000Z 1/Mon 1581940800
# 2020-02-21T00:00:00.000Z 5/Fri 1582243200
# 2020-02-21T12:00:00.000Z 5/Fri 1582286400 <- end


#
# rq.tariff_zone must be == rule.tariffzone
#
@pytest.mark.servicetest
async def test_tariff_zone_unset(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {'reference_time': '2020-02-12T12:00:00.000Z', 'time_zone': 'UTC'},
    )
    assert response.status_code == 200
    assert (
        len(get_ids(response)) > 30
    )  # will contains almost all entries in base


@pytest.mark.servicetest
async def test_tariff_zone_good(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tz',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000101',
        '000000000000000000000102',
    }


@pytest.mark.servicetest
async def test_tariff_zone_bad(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'zzz',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == set()


#
# driver_branding = full_branding:
#   branding_type (- [full_branding, sticker] || undefined
# driver_branding != full_branding:
#   branding_type == driver_branding || undefined
#
@pytest.mark.servicetest
async def test_driver_branding_unset(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_db',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000201',  # null
        '000000000000000000000202',  # sticker
        '000000000000000000000203',  # full_branding
        '000000000000000000000204',  # no_branding
        '000000000000000000000205',  # lightbox
    }


@pytest.mark.servicetest
async def test_driver_branding_sticker(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_db',
            'driver_branding': 'sticker',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000201',  # null
        '000000000000000000000202',  # sticker
    }


@pytest.mark.servicetest
async def test_driver_branding_full(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_db',
            'driver_branding': 'full_branding',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000201',  # null
        '000000000000000000000202',  # sticker
        '000000000000000000000203',  # full_branding
        '000000000000000000000205',  # lightbox
    }


@pytest.mark.servicetest
async def test_driver_branding_nobrand(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_db',
            'driver_branding': 'no_branding',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000201',  # null
        '000000000000000000000204',  # no_branding
    }


@pytest.mark.servicetest
async def test_driver_branding_bad(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_db',
            'driver_branding': 'zzz',
        },
    )
    assert response.status_code == 400


#
# profile_payment_type
#  PPTR ::= rq.profile_payment_type_restrictions
#  PPTR unset ==> undef, any, none, cash, online
#  PPTR == none -> undef, any, none, cash, online
#  PPTR == cash -> undef, any, cash
#  PPTR == online -> undef, any, online
#
@pytest.mark.servicetest
async def test_profile_payment_type_unset(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ppt',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000301',  # undef
        '000000000000000000000302',  # any
        '000000000000000000000303',  # none
        '000000000000000000000304',  # cash
        '000000000000000000000305',  # online
    }


@pytest.mark.servicetest
async def test_profile_payment_type_none(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ppt',
            'profile_payment_type_restrictions': 'none',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000301',  # undef
        '000000000000000000000302',  # any
        '000000000000000000000303',  # none
        '000000000000000000000304',  # cash
        '000000000000000000000305',  # online
    }


@pytest.mark.servicetest
async def test_profile_payment_type_cash(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ppt',
            'profile_payment_type_restrictions': 'cash',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000301',  # undef
        '000000000000000000000302',  # any
        '000000000000000000000304',  # cash
    }


@pytest.mark.servicetest
async def test_profile_payment_type_online(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ppt',
            'profile_payment_type_restrictions': 'online',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000301',  # undef
        '000000000000000000000302',  # any
        '000000000000000000000305',  # online
    }


@pytest.mark.servicetest
async def test_profile_payment_type_bad(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ppt',
            'profile_payment_type_restrictions': 'zzz',
        },
    )
    assert response.status_code == 400


#
# payment_type: undef - no restrictions
# else: rules undef || ==payment_type
#
@pytest.mark.servicetest
async def test_order_payment_type_undef(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_opt',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000401',  # undef
        '000000000000000000000402',  # cash
        '000000000000000000000403',  # card
    }


@pytest.mark.servicetest
async def test_order_payment_type_cash(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_opt',
            'order_payment_type': 'cash',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000401',  # undef
        '000000000000000000000402',  # cash
    }


@pytest.mark.servicetest
async def test_order_payment_type_card(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_opt',
            'order_payment_type': 'card',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000401',  # undef
        '000000000000000000000403',  # card
    }


@pytest.mark.servicetest
async def test_order_payment_type_zzz(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_opt',
            'order_payment_type': 'zzz',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'000000000000000000000401'}  # undef


#
# geoareas == undef : no restrictions
# else rq.geoareas x rule.geoareas != []
#
@pytest.mark.servicetest
async def test_geoareas_undef(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ga',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000501',  # undef
        '000000000000000000000502',  # []
        '000000000000000000000503',  # a
        '000000000000000000000504',  # b
        '000000000000000000000505',  # c
        '000000000000000000000506',  # a, b
        '000000000000000000000507',  # a, c
        '000000000000000000000508',  # b, c
        '000000000000000000000509',  # a, b, c
    }


@pytest.mark.servicetest
async def test_geoareas_zone_abc(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ga',
            'geoareas': ['a', 'b', 'c'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000501',  # undef
        '000000000000000000000502',  # []
        '000000000000000000000503',  # a
        '000000000000000000000504',  # b
        '000000000000000000000505',  # c
        '000000000000000000000506',  # a, b
        '000000000000000000000507',  # a, c
        '000000000000000000000508',  # b, c
        '000000000000000000000509',  # a, b, c
    }


@pytest.mark.servicetest
async def test_geoareas_zone_a(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ga',
            'geoareas': ['a'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000501',  # undef
        '000000000000000000000502',  # []
        '000000000000000000000503',  # a
        '000000000000000000000506',  # a, b
        '000000000000000000000507',  # a, c
        '000000000000000000000509',  # a, b, c
    }


@pytest.mark.servicetest
async def test_geoareas_zone_b(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ga',
            'geoareas': ['b'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000501',  # undef
        '000000000000000000000502',  # []
        '000000000000000000000504',  # b
        '000000000000000000000506',  # a, b
        '000000000000000000000508',  # b, c
        '000000000000000000000509',  # a, b, c
    }


@pytest.mark.servicetest
async def test_geoareas_zone_c(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ga',
            'geoareas': ['c'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000501',  # undef
        '000000000000000000000502',  # []
        '000000000000000000000505',  # c
        '000000000000000000000507',  # a, c
        '000000000000000000000508',  # b, c
        '000000000000000000000509',  # a, b, c
    }


@pytest.mark.servicetest
async def test_geoareas_ab(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ga',
            'geoareas': ['a', 'b'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000501',  # undef
        '000000000000000000000502',  # []
        '000000000000000000000503',  # a
        '000000000000000000000504',  # b
        '000000000000000000000506',  # a, b
        '000000000000000000000507',  # a, c
        '000000000000000000000508',  # b, c
        '000000000000000000000509',  # a, b, c
    }


@pytest.mark.servicetest
async def test_geoareas_zzz(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ga',
            'geoareas': ['zzz'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000501',  # undef
        '000000000000000000000502',  # []
    }


#
# time constraints
# rq.reference_time required
# rq.time_zone required
# rq.reference_time < rule.end
# rule.weekday == [] or [dow(rq.reference_time)] x rule.weekday != []
# rule.hour == [] or [hour(rq.reference_time)] x rule.hour != []
#


@pytest.mark.servicetest
async def test_reference_time_unset(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE, {'time_zone': 'UTC', 'zone_name': 'test_tt'},
    )
    assert response.status_code == 400


@pytest.mark.servicetest
async def test_time_zone_unset(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {'reference_time': '2020-02-12T12:00:00.000Z', 'zone_name': 'test_tt'},
    )
    assert response.status_code == 400


@pytest.mark.servicetest
async def test_time_match_utc(taxi_billing_subventions_x):
    # 2020-02-12T12:00:00.000Z 3/Wed 1581508800 <- check
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tt',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000601',  # weekday:[], hour:[]
        '000000000000000000000602',  # weekday:[2,3], hour:[]
        '000000000000000000000603',  # weekday:[], hour:[12]
    }


@pytest.mark.servicetest
async def test_time_match_utc3(taxi_billing_subventions_x):
    # 2020-02-12T12:00:00.000Z 3/Wed 1581508800 <- check
    # ... Europe/Moscow      = 15:00:00
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'Europe/Moscow',
            'zone_name': 'test_tt',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000601',  # weekday:[], hour:[]
        '000000000000000000000602',  # weekday:[2,3], hour:[]
        '000000000000000000000604',  # weekday:[], hour:[15,16]
    }


@pytest.mark.servicetest
async def test_time_match_utc5(taxi_billing_subventions_x):
    # 2020-02-12T12:00:00.000Z 3/Wed 1581508800 <- check
    # ... Europe/Moscow      = 15:00:00
    # ... Asia/Yekaterinburg = 17:00:00
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'test_tt',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000601',  # weekday:[], hour:[]
        '000000000000000000000602',  # weekday:[2,3], hour:[]
        '000000000000000000000605',  # weekday:[], hour:[17,18]
        '000000000000000000000606',  # weekday:[3], hour:[17]
    }


@pytest.mark.servicetest
async def test_time_match_over(taxi_billing_subventions_x):
    # 2020-02-21T12:00:00.000Z 5/Fri 1582286400 <- end
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-21T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tt',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == set()


#
#
#
@pytest.mark.servicetest
async def test_profile_tags_unset(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000701',  # on_top, undef
        '000000000000000000000702',  # on_top, [tag1]
        '000000000000000000000703',  # on_top, [tag2]
        '000000000000000000000704',  # on_top, [tag1, tag2]
        '000000000000000000000711',  # [z] mfg_geo
        '000000000000000000000712',  # [z] on_top_geo
        '000000000000000000000713',  # [z] mfg
        '000000000000000000000714',  # [z] on_top
        'group715',  # [z] nmfg
        'group716',  # [z] do_x_get_y
        '000000000000000000000718',  # [z] booking_geo_on_top
        '000000000000000000000719',  # [z] booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_profile_tags_tag1(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['tag1'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000701',  # on_top, undef
        '000000000000000000000702',  # on_top, [tag1]
        '000000000000000000000704',  # on_top, [tag1, tag2]
    }


@pytest.mark.servicetest
async def test_profile_tags_tag123(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['tag1', 'tag2', 'tag3'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000701',  # on_top, undef
        '000000000000000000000702',  # on_top, [tag1]
        '000000000000000000000703',  # on_top, [tag2]
        '000000000000000000000704',  # on_top, [tag1, tag2]
    }


@pytest.mark.servicetest
async def test_profile_tags_empty(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': [],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'000000000000000000000701'}  # on_top, undef


@pytest.mark.servicetest
async def test_profile_tags_z(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['z'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000701',  # on_top, undef
        '000000000000000000000711',  # [z] mfg_geo
        '000000000000000000000712',  # [z] on_top_geo
        '000000000000000000000713',  # [z] mfg
        '000000000000000000000714',  # [z] on_top
        'group715',  # [z] nmfg
        'group716',  # [z] do_x_get_y
        '000000000000000000000718',  # [z] booking_geo_on_top
        '000000000000000000000719',  # [z] booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_profile_tags_disable_mfg_geo(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['z', 'subv_disable_mfg_geo'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000701',  # on_top, undef
        '000000000000000000000712',  # [z] on_top_geo
        '000000000000000000000713',  # [z] mfg
        '000000000000000000000714',  # [z] on_top
        'group715',  # [z] nmfg
        'group716',  # [z] do_x_get_y
        '000000000000000000000718',  # [z] booking_geo_on_top
        '000000000000000000000719',  # [z] booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_profile_tags_disable_on_top_geo(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['z', 'subv_disable_on_top_geo'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000701',  # on_top, undef
        '000000000000000000000711',  # [z] mfg_geo
        '000000000000000000000713',  # [z] mfg
        '000000000000000000000714',  # [z] on_top
        'group715',  # [z] nmfg
        'group716',  # [z] do_x_get_y
        '000000000000000000000718',  # [z] booking_geo_on_top
        '000000000000000000000719',  # [z] booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_profile_tags_disable_mfg(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['z', 'subv_disable_mfg'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000701',  # on_top, undef
        '000000000000000000000711',  # [z] mfg_geo
        '000000000000000000000712',  # [z] on_top_geo
        '000000000000000000000714',  # [z] on_top
        'group715',  # [z] nmfg
        'group716',  # [z] do_x_get_y
        '000000000000000000000718',  # [z] booking_geo_on_top
        '000000000000000000000719',  # [z] booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_profile_tags_disable_on_top(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['z', 'subv_disable_on_top'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000711',  # [z] mfg_geo
        '000000000000000000000712',  # [z] on_top_geo
        '000000000000000000000713',  # [z] mfg
        'group715',  # [z] nmfg
        'group716',  # [z] do_x_get_y
        '000000000000000000000718',  # [z] booking_geo_on_top
        '000000000000000000000719',  # [z] booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_profile_tags_disable_nmfg(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['z', 'subv_disable_nmfg'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000701',  # on_top, undef
        '000000000000000000000711',  # [z] mfg_geo
        '000000000000000000000712',  # [z] on_top_geo
        '000000000000000000000713',  # [z] mfg
        '000000000000000000000714',  # [z] on_top
        'group716',  # [z] do_x_get_y
        '000000000000000000000718',  # [z] booking_geo_on_top
        '000000000000000000000719',  # [z] booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_profile_tags_disable_do_x_get_y(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['z', 'subv_disable_do_x_get_y'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000701',  # on_top, undef
        '000000000000000000000711',  # [z] mfg_geo
        '000000000000000000000712',  # [z] on_top_geo
        '000000000000000000000713',  # [z] mfg
        '000000000000000000000714',  # [z] on_top
        'group715',  # [z] nmfg
        '000000000000000000000718',  # [z] booking_geo_on_top
        '000000000000000000000719',  # [z] booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_profile_tags_disable_all(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_tags',
            'tags': ['z', 'subv_disable_all'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == set()


@pytest.mark.servicetest
async def test_types_filtering(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_types',
            'rule_types': [
                'mfg',
                'on_top',
                'do_x_get_y',
                'booking_geo',
                'driver_fix',
                'nmfg',
            ],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000801',  # mfg_geo
        '000000000000000000000802',  # on_top_geo
        '000000000000000000000803',  # mfg
        '000000000000000000000804',  # on_top
        'group805',  # nmfg
        'group806',  # do_x_get_y
        '000000000000000000000808',  # booking_geo_on_top
        '000000000000000000000809',  # booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_types_filtering_mfg(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_types',
            'rule_types': ['mfg'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000801',  # mfg_geo
        '000000000000000000000803',  # mfg
    }


@pytest.mark.servicetest
async def test_types_filtering_on_top(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_types',
            'rule_types': ['on_top'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000802',  # on_top_geo
        '000000000000000000000804',  # on_top
    }


@pytest.mark.servicetest
async def test_types_filtering_booking_geo(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_types',
            'rule_types': ['booking_geo'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000808',  # booking_geo_on_top
        '000000000000000000000809',  # booking_geo_guarantee
    }


@pytest.mark.servicetest
async def test_types_filtering_nmfg(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_types',
            'rule_types': ['nmfg'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'group805'}  # nmfg


@pytest.mark.servicetest
async def test_profile_tariff_classes_unset(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ptc',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000901',  # booking_geo, class=[]
        '000000000000000000000903',  # mfg, class=[]
        '000000000000000000000904',  # booking_geo, class=[a, b]
        '000000000000000000000906',  # mfg, class=[a, b]
    }


@pytest.mark.servicetest
async def test_profile_tariff_classes_a(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ptc',
            'profile_tariff_classes': ['a'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000901',  # booking_geo, class=[]
        '000000000000000000000903',  # mfg, class=[]
        '000000000000000000000904',  # booking_geo, class=[a, b]
        '000000000000000000000906',  # mfg, class=[a, b]
    }


@pytest.mark.servicetest
async def test_profile_tariff_classes_abc(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_ptc',
            'profile_tariff_classes': ['a', 'b', 'c'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000000901',  # booking_geo, class=[]
        '000000000000000000000903',  # mfg, class=[]
        '000000000000000000000904',  # booking_geo, class=[a, b]
        '000000000000000000000906',  # mfg, class=[a, b]
    }


@pytest.mark.servicetest
async def test_order_tariff_classes_unset(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_otc',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000001001',  # mfg, class=[]
        '000000000000000000001002',  # mfg, class=[a, b]
    }


@pytest.mark.servicetest
async def test_order_tariff_classes_a(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_otc',
            'tariff_class': 'a',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000001001',  # mfg, class=[]
        '000000000000000000001002',  # mfg, class=[a, b]
    }


@pytest.mark.servicetest
async def test_order_tariff_classes_c(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_otc',
            'tariff_class': 'c',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'000000000000000000001001'}  # mfg, class=[]


@pytest.mark.servicetest
async def test_rule_status(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-12T12:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'test_rs',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        '000000000000000000001101',  # mfg, status unset
        '000000000000000000001102',  # mfg, status approved
    }
