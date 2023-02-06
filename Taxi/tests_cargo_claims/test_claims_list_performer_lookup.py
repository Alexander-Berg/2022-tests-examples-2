# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines

import datetime
import json
import uuid

import pytest

from testsuite.utils import matching


_CARGO_EXTENDED_LOOKUP_MERGE_TAG = [
    {
        'consumer': 'cargo-claims/segment-info',
        'merge_method': 'dicts_recursive_merge',
        'tag': 'cargo_extended_lookup',
    },
    {
        'consumer': 'cargo-claims/active-performer-lookup-claims-cache',
        'merge_method': 'dicts_recursive_merge',
        'tag': 'cargo_extended_lookup',
    },
]


def _build_settings(
        *,
        cargo_claims_cache_enabled=True,
        special_requirements_enabled=False,
        response_chunk_size=None,
        pg_chunk_size=2,
        response_chunk_throttling_ms=None,
):
    return {
        'calculate_ignorable_special_requirements': (
            special_requirements_enabled
        ),
        'candidates_cache_enabled': False,
        'cargo_claims_cache_enabled': cargo_claims_cache_enabled,
        'delay_claims_settings': {
            'not_actual_after_due_sec': 3600,
            'not_actual_before_due_sec': 1800,
        },
        'soon_claims_settings': {
            'not_actual_after_last_status_change_sec': 3600,
        },
        'response_chunk_size': response_chunk_size,
        'pg_chunk_size': pg_chunk_size,
        'response_chunk_throttling_ms': response_chunk_throttling_ms,
    }


def _get_claim_ids(response):
    return {c['claim_id'] for c in response.json()['claims']}


def _insert_claim_segments(
        cursor,
        claim_id,
        claim_uuid,
        cargo_order_ids=None,
        spec_requirements=None,
        created_ts=None,
):
    if created_ts is None:
        created_ts = datetime.datetime.now(datetime.timezone.utc)
    spec_requirements = (
        spec_requirements
        if spec_requirements is not None
        else {'virtual_tariffs': []}
    )
    if cargo_order_ids is None:
        cargo_order_ids = [None]
    segment_ids = []
    for cargo_order_id in cargo_order_ids:
        cursor.execute(
            'INSERT INTO cargo_claims.claim_segments '
            '(claim_id, claim_uuid, uuid, '
            ' cargo_order_id, special_requirements,'
            ' created_ts) '
            'VALUES (%(claim_id)s, %(claim_uuid)s, '
            '        %(segment_uuid)s, %(cargo_order_id)s, '
            '        %(special_requirements)s, %(created_ts)s)'
            'RETURNING claim_segments.uuid',
            dict(
                claim_id=claim_id,
                claim_uuid=claim_uuid,
                segment_uuid=str(uuid.uuid4()),
                cargo_order_id=cargo_order_id,
                special_requirements=json.dumps(spec_requirements),
                created_ts=str(created_ts),
            ),
        )
        segment_ids.append(str(cursor.fetchone()[0]))
    return segment_ids


def _insert_claim(
        cursor,
        status,
        is_delayed,
        last_status_change_ts,
        due,
        *,
        taxi_class='express',
        taxi_classes=None,
        lookup_ttl=None,
        cargo_order_ids=None,
        virtual_tariffs=None,
):
    now = datetime.datetime.now(datetime.timezone.utc)
    created = now - datetime.timedelta(hours=5)
    corp_client_id = str(uuid.uuid4()).replace('-', '')
    claim_uuid = str(uuid.uuid4()).replace('-', '')
    is_delayed = 'TRUE' if is_delayed else 'FALSE'
    due = f'\'{due.isoformat()}\'' if due else 'NULL'
    cursor.execute(
        f'INSERT INTO cargo_claims.claims '
        f'(corp_client_id, status, uuid_id,'
        f'zone_id, emergency_fullname,'
        f'emergency_personal_phone_id, idempotency_token, '
        f'updated_ts, created_ts, last_status_change_ts, is_delayed, due) '
        f'VALUES ('
        f'  \'{corp_client_id}\', '
        f'  \'{status}\', '
        f'  \'{claim_uuid}\', '
        f'  \'moscow\', '
        f'  \'emergency_name\', '
        f'  \'+79098887777_id\', '
        f'  \'idempotency_token_hardcode_1\', '
        f'  \'{now}\','
        f'  \'{created}\','
        f'  \'{last_status_change_ts}\','
        f'    {is_delayed},'
        f'    {due}'
        f'  )',
    )
    assert cursor.rowcount == 1
    cursor.execute(
        f'SELECT id FROM cargo_claims.claims '
        f'WHERE uuid_id = \'{claim_uuid}\';',
    )
    claim_id = cursor.fetchall()[0][0]
    segment_uuid = _insert_claim_segments(
        cursor,
        claim_id,
        claim_uuid,
        cargo_order_ids=cargo_order_ids,
        spec_requirements=virtual_tariffs,
        created_ts=last_status_change_ts - datetime.timedelta(seconds=10),
    )[0]
    _insert_matched_cars(cursor, claim_uuid, taxi_class=taxi_class)
    if taxi_classes:
        _insert_additional_info(
            cursor,
            claim_id,
            claim_uuid,
            taxi_class=taxi_class,
            taxi_classes=taxi_classes,
            lookup_ttl=lookup_ttl,
        )
    return claim_uuid, segment_uuid


def _insert_claim_audit(cursor, claim_id, claim_uuid, acceptance_time):
    cursor.execute(
        f'INSERT INTO cargo_claims.claim_audit '
        f'(old_status, new_status, claim_id, claim_uuid, event_time) '
        f'VALUES ('
        f'  \'ready_for_approval\','
        f'  \'accepted\','
        f'  {claim_id},'
        f'  {claim_uuid},'
        f'  \'{acceptance_time}\''
        f')',
    )
    assert cursor.rowcount == 1
    cursor.execute(
        f'DELETE FROM cargo_claims.claim_audit '
        f'WHERE claim_uuid = {claim_uuid} and '
        f'new_status = \'performer_lookup\'',
    )
    cursor.execute(
        f'INSERT INTO cargo_claims.claim_audit '
        f'(old_status, new_status, claim_id, claim_uuid, event_time) '
        f'VALUES ('
        f'  \'accepted\','
        f'  \'performer_lookup\','
        f'  {claim_id},'
        f'  {claim_uuid},'
        f'  \'{acceptance_time + datetime.timedelta(seconds=3)}\''
        f')',
    )
    assert cursor.rowcount == 1
    cursor.execute(
        f'INSERT INTO cargo_claims.claim_audit '
        f'(old_status, new_status, claim_id, claim_uuid, event_time) '
        f'VALUES ('
        f'  \'accepted\','
        f'  \'performer_lookup\','
        f'  {claim_id},'
        f'  {claim_uuid},'
        f'  \'{acceptance_time + datetime.timedelta(seconds=5)}\''
        f')',
    )
    assert cursor.rowcount == 1
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.claim_audit
        (old_status, new_status, claim_id, claim_uuid, event_time)
        VALUES (
            \'accepted\',
            \'performer_lookup\',
            \'{claim_id}\',
            \'{claim_uuid}\',
            \'{acceptance_time + datetime.timedelta(days=99)}\'
        )""",
    )
    assert cursor.rowcount == 1


def _insert_matched_cars(cursor, claim_id, *, taxi_class='express'):
    cursor.execute(
        f'INSERT INTO cargo_claims.matched_cars '
        f'(cargo_claim_id, claim_uuid, taxi_class) '
        f'VALUES ( %s, %s, %s)',
        (claim_id, claim_id, taxi_class),
    )
    assert cursor.rowcount == 1


def _insert_additional_info(
        cursor,
        claim_id,
        claim_uuid,
        *,
        taxi_class='express',
        taxi_classes=None,
        lookup_ttl=None,
):
    cursor.execute(
        f'INSERT INTO cargo_claims.additional_info '
        f'(claim_id, claim_uuid, taxi_class, taxi_classes, lookup_ttl) '
        f'VALUES ( %s, %s, %s, %s, %s )',
        (claim_id, claim_uuid, taxi_class, taxi_classes, lookup_ttl),
    )
    assert cursor.rowcount == 1


def _insert_claim_estimation(cursor, claim_id, taxi_classes_substitution):
    if taxi_classes_substitution is None:
        substitution = 'NULL'
    else:
        words = ['\'' + cls + '\'' for cls in taxi_classes_substitution]
        substitution = 'ARRAY[' + ', '.join(words) + ']::text[]'
    cursor.execute(
        f'INSERT INTO cargo_claims.claim_estimating_results '
        f'(status, cargo_claim_id, claim_uuid, taxi_classes_substitution) '
        f'VALUES (\'succeed\', \'{claim_id}\','
        f'\'{claim_id}\', {substitution})',
    )
    assert cursor.rowcount == 1


async def test_active_claims_selection(
        taxi_cargo_claims, claims_exp_extended_tariffs, pgsql,
):
    await claims_exp_extended_tariffs()

    # Fill cache
    cursor = pgsql['cargo_claims'].cursor()
    #  Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    _, soon_1 = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    _, soon_2 = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    _, soon_accepted = _insert_claim(
        cursor, 'accepted', False, now - datetime.timedelta(minutes=1), None,
    )
    assert soon_accepted  # unused is OK
    _, soon_too_old = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(hours=3),
        None,
    )
    assert soon_too_old  # unused is OK
    _, delayed_1 = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(minutes=5),
    )
    _, delayed_accepted = _insert_claim(
        cursor,
        'accepted',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(minutes=5),
    )
    assert delayed_accepted  # unused is OK
    _, delayed_too_old = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now - datetime.timedelta(minutes=777),
    )
    assert delayed_too_old  # unused is OK
    _, delayed_too_young = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(minutes=555),
    )
    assert delayed_too_young  # unused is OK
    #  Invalidate
    await taxi_cargo_claims.invalidate_caches()

    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = {c['claim_id'] for c in response.json()['claims']}

    assert response_claims == {soon_1, soon_2, delayed_1}


async def test_enable_config_on(
        taxi_cargo_claims, claims_exp_extended_tariffs, pgsql,
):
    await claims_exp_extended_tariffs()

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    resp_body = response.json()
    assert len(resp_body['claims']) == 1
    assert resp_body['claims'][0]['ignorable_special_requirements'] == []


@pytest.mark.config(
    CARGO_CANDIDATES_ACTIVE_CLAIMS_CACHE_SETTINGS=_build_settings(
        cargo_claims_cache_enabled=False,
    ),
)
async def test_config_off(
        taxi_cargo_claims, claims_exp_extended_tariffs, pgsql,
):
    await claims_exp_extended_tariffs()

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    assert not response.json()['claims']


@pytest.fixture(name='claims_exp_extended_tariffs')
def _claims_exp_extended_tariffs(taxi_cargo_claims, exp_extended_tariffs):
    async def _wrapper(**kwargs):
        await exp_extended_tariffs(
            taxi_cargo_claims,
            consumers=['cargo-claims/active-performer-lookup-claims-cache'],
            **kwargs,
        )

    return _wrapper


@pytest.fixture(name='exp_ignorable_special_requirements')
def _exp_ignorable_special_requirements(taxi_cargo_claims, experiments3):
    async def _wrapper(*, ignorable_special_requirements):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_ignorable_special_requirements',
            consumers=['cargo-claims/active-performer-lookup-claims-cache'],
            clauses=[],
            default_value={
                'exp_spec_reqs': {
                    'ignorable_special_requirements': (
                        ignorable_special_requirements
                    ),
                },
            },
            merge_values_by=_CARGO_EXTENDED_LOOKUP_MERGE_TAG,
        )
        await taxi_cargo_claims.invalidate_caches()

    return _wrapper


async def test_basic_limit_allowed_classes(
        taxi_cargo_claims, pgsql, claims_exp_extended_tariffs,
):
    await claims_exp_extended_tariffs()

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    soon_claim_uuid, soon_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    _insert_claim_estimation(
        cursor, soon_claim_uuid, ['courier', 'express', 'cargo'],
    )
    delayed_claim_uuid, delayed_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=1000),
    )
    _insert_claim_estimation(
        cursor, delayed_claim_uuid, ['courier', 'express'],
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = {
        c['claim_id']: set(c.get('allowed_classes'))
        for c in response.json()['claims']
    }
    assert response_claims == {
        soon_uuid: {'express', 'cargo'},
        delayed_uuid: {'express'},
    }


async def test_experiment_off(
        taxi_cargo_claims, pgsql, claims_exp_extended_tariffs,
):
    await claims_exp_extended_tariffs(enabled=False)

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    soon_claim_uuid, soon_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    _insert_claim_estimation(
        cursor, soon_claim_uuid, ['courier', 'express', 'cargo'],
    )
    delayed_claim_uuid, delayed_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=1000),
    )
    _insert_claim_estimation(
        cursor, delayed_claim_uuid, ['courier', 'express'],
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = {
        c['claim_id']: set(c.get('allowed_classes', ['_no_limits_']))
        for c in response.json()['claims']
    }
    assert response_claims.get(soon_uuid, {'_no_limits_'}) == {'_no_limits_'}
    assert response_claims.get(delayed_uuid, {'_no_limits_'}) == {
        '_no_limits_',
    }


@pytest.mark.parametrize(
    'seconds_since_drafted, expected_allowed_classes',
    [
        (801, {'express', 'cargo'}),
        (999, {'_no_limits_'}),
        (7200, None),  # too far to be in cache
    ],
)
async def test_limit_allowed_classes_soon_lags(
        taxi_cargo_claims,
        pgsql,
        claims_exp_extended_tariffs,
        seconds_since_drafted,
        expected_allowed_classes,
):
    await claims_exp_extended_tariffs()

    # Add claims
    cursor = pgsql['cargo_claims'].cursor()
    now = datetime.datetime.now(datetime.timezone.utc)
    soon_claim_uuid, soon_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(seconds=seconds_since_drafted),
        None,
    )
    _insert_claim_estimation(
        cursor, soon_claim_uuid, ['courier', 'express', 'cargo'],
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = {
        c['claim_id']: set(c.get('allowed_classes', ['_no_limits_']))
        for c in response.json()['claims']
    }
    if expected_allowed_classes is None:
        assert response_claims == {}
    else:
        assert response_claims == {soon_uuid: expected_allowed_classes}


@pytest.mark.parametrize(
    'seconds_before_due, expected_allowed_classes',
    [
        (7200, None),  # too far to be in cache
        (999, {'express'}),
        (600, {'courier', 'express'}),
        (401, {'_no_limits_'}),
        (-100, {'_no_limits_'}),
        (-7200, None),  # too far to be in cache
    ],
)
async def test_limit_allowed_classes_delayed_lags(
        taxi_cargo_claims,
        pgsql,
        claims_exp_extended_tariffs,
        seconds_before_due,
        expected_allowed_classes,
):
    await claims_exp_extended_tariffs(
        extra_delayed_classes=[
            {
                'taxi_classes': ['cargo'],
                'delay': {'since_lookup': 450, 'since_due': -450},
            },
        ],
    )

    # Add claims
    cursor = pgsql['cargo_claims'].cursor()
    now = datetime.datetime.now(datetime.timezone.utc)
    delayed_claim_uuid, delayed_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=seconds_before_due),
    )
    _insert_claim_estimation(
        cursor, delayed_claim_uuid, ['courier', 'express', 'cargo'],
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = {
        c['claim_id']: set(c.get('allowed_classes', ['_no_limits_']))
        for c in response.json()['claims']
    }
    if expected_allowed_classes is None:
        assert response_claims == {}
    else:
        assert response_claims == {delayed_uuid: expected_allowed_classes}


# for newway different logic
async def test_allowed_classes_intersections(
        taxi_cargo_claims, pgsql, claims_exp_extended_tariffs,
):
    await claims_exp_extended_tariffs(delayed_classes=['econom'])

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    soon_claim_uuid, soon_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    _insert_claim_estimation(cursor, soon_claim_uuid, ['vip'])
    delayed_claim_uuid, delayed_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=1000),
    )
    _insert_claim_estimation(cursor, delayed_claim_uuid, ['vip', 'econom'])
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = {
        c['claim_id']: set(c.get('allowed_classes', ['_no_limits_']))
        for c in response.json()['claims']
    }
    assert response_claims == {
        soon_uuid: {'_no_limits_'},
        delayed_uuid: {'express', 'vip'},
    }


@pytest.mark.parametrize(
    'substitution, expected_allowed_classes',
    [
        (['express', 'cargo', 'econom'], {'_no_limits_'}),
        (
            ['express', 'vip', 'cargo', 'econom'],
            {'express', 'cargo', 'econom'},
        ),
        (['express'], {'_no_limits_'}),  # can not limit single class
        (None, {'_no_limits_'}),  # no substitution => no limit
        ([], {'_no_limits_'}),  # incorrect substitution => no limit
    ],
)
async def test_misc_substitutions(
        taxi_cargo_claims,
        pgsql,
        claims_exp_extended_tariffs,
        substitution,
        expected_allowed_classes,
):
    await claims_exp_extended_tariffs(delayed_classes=['vip'])

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    soon_claim_uuid, soon_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    _insert_claim_estimation(cursor, soon_claim_uuid, substitution)
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = {
        c['claim_id']: set(c.get('allowed_classes', ['_no_limits_']))
        for c in response.json()['claims']
    }
    assert response_claims == {soon_uuid: expected_allowed_classes}


async def test_extend_cache_by_cargo_orders_id(
        taxi_cargo_claims, pgsql, claims_exp_extended_tariffs,
):
    await claims_exp_extended_tariffs()

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    soon_cargo_order_1_1 = str(uuid.uuid4())
    soon_cargo_order_1_2 = str(uuid.uuid4())
    soon_cargo_order_2_1 = str(uuid.uuid4())
    soon_claim_uuid_1, _ = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
        cargo_order_ids=[soon_cargo_order_1_1, soon_cargo_order_1_2],
    )
    _insert_claim_estimation(
        cursor, soon_claim_uuid_1, ['courier', 'express', 'cargo'],
    )
    soon_claim_uuid_2, _ = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
        cargo_order_ids=[soon_cargo_order_1_1, soon_cargo_order_2_1],
    )
    _insert_claim_estimation(
        cursor, soon_claim_uuid_2, ['courier', 'express', 'cargo'],
    )
    delayed_claim_uuid_1, delayed_uuid_1 = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=1000),
    )
    _insert_claim_estimation(
        cursor, delayed_claim_uuid_1, ['courier', 'express'],
    )
    delayed_cargo_order_2_1 = str(uuid.uuid4())
    delayed_claim_uuid_2, _ = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=1000),
        cargo_order_ids=[delayed_cargo_order_2_1],
    )
    _insert_claim_estimation(
        cursor, delayed_claim_uuid_2, ['courier', 'express'],
    )
    delayed_claim_uuid_3, _ = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=1000),
        cargo_order_ids=[delayed_cargo_order_2_1],
    )
    _insert_claim_estimation(
        cursor, delayed_claim_uuid_3, ['courier', 'express'],
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = {
        c['claim_id']: set(c.get('allowed_classes'))
        for c in response.json()['claims']
    }
    assert response_claims[f'order/{soon_cargo_order_1_1}'] == {
        'express',
        'cargo',
    }
    assert response_claims[f'order/{soon_cargo_order_1_2}'] == {
        'express',
        'cargo',
    }
    assert response_claims[f'order/{soon_cargo_order_2_1}'] == {
        'express',
        'cargo',
    }
    assert response_claims[delayed_uuid_1] == {'express'}
    assert response_claims[f'order/{delayed_cargo_order_2_1}'] == {'express'}


async def test_ignorable_special_requirements(
        taxi_cargo_claims,
        pgsql,
        claims_exp_extended_tariffs,
        exp_ignorable_special_requirements,
        experiments3,
):
    await claims_exp_extended_tariffs(delayed_classes=['express'])
    await exp_ignorable_special_requirements(
        ignorable_special_requirements=[
            {
                'taxi_classes': ['courier'],
                'requirements': ['thermal', 'bag'],
                'delay': {'since_lookup': 0, 'since_due': -100500},
            },
        ],
    )
    exp3_ignorable_specreq_recorder = experiments3.record_match_tries(
        'cargo_ignorable_special_requirements',
    )

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    virtual_tariffs = {
        'virtual_tariffs': [
            {
                'class': 'courier',
                'special_requirements': [{'id': 'spec1'}, {'id': 'spec2'}],
            },
            {
                'class': 'cargo',
                'special_requirements': [{'id': 'spec1'}, {'id': 'spec3'}],
            },
        ],
    }
    delayed_claim_uuid_1, _ = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=1000),
        taxi_class='courier',
        cargo_order_ids=[str(uuid.uuid4()), str(uuid.uuid4())],
        virtual_tariffs=virtual_tariffs,
    )
    _insert_claim_estimation(
        cursor, delayed_claim_uuid_1, ['courier', 'express'],
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    resp_body = response.json()
    spec_requirements = resp_body['claims'][0][
        'ignorable_special_requirements'
    ][0]['requirements']
    spec_requirements.sort()
    assert resp_body['claims'][0] == {
        'claim_id': matching.AnyString(),
        'allowed_classes': ['courier'],
        'ignorable_special_requirements': [
            {'tariff_class': 'courier', 'requirements': ['bag', 'thermal']},
        ],
    }
    match_tries = await exp3_ignorable_specreq_recorder.get_match_tries(
        ensure_ntries=2,
    )
    kwargs_requirements = match_tries[0].kwargs['special_requirements']
    assert sorted(kwargs_requirements) == ['spec1', 'spec2', 'spec3']


async def test_ignorable_special_requirements_finally(
        taxi_cargo_claims,
        pgsql,
        claims_exp_extended_tariffs,
        exp_ignorable_special_requirements,
):
    """
    After all time intervals fallback in router field
    """
    await claims_exp_extended_tariffs(delayed_classes=['express'])
    await exp_ignorable_special_requirements(
        ignorable_special_requirements=[
            {
                'taxi_classes': ['courier'],
                'requirements': ['thermal', 'bag'],
                'delay': {'since_lookup': 0, 'since_due': -100500},
            },
            {
                'taxi_classes': ['courier'],
                'requirements': ['fallback'],
                'delay': {'since_lookup': 900, 'since_due': -900},
            },
        ],
    )

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    delayed_claim_uuid_1, _ = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=500),
    )
    _insert_claim_estimation(
        cursor, delayed_claim_uuid_1, ['courier', 'express'],
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['claims']
    ignorable_special_requirements = resp_body['claims'][0].get(
        'ignorable_special_requirements',
    )
    assert len(ignorable_special_requirements) == 1
    assert ignorable_special_requirements[0]['tariff_class'] == 'courier'
    assert set(ignorable_special_requirements[0]['requirements']) == {
        'thermal',
        'bag',
        'fallback',
    }


@pytest.mark.config(
    CARGO_CANDIDATES_ACTIVE_CLAIMS_CACHE_SETTINGS=_build_settings(
        special_requirements_enabled=False,
    ),
)
async def test_disable_ignorable_requirements_processing(
        taxi_cargo_claims,
        pgsql,
        claims_exp_extended_tariffs,
        exp_ignorable_special_requirements,
):
    await claims_exp_extended_tariffs(delayed_classes=['express'])
    await exp_ignorable_special_requirements(
        ignorable_special_requirements=[
            {
                'taxi_classes': ['courier'],
                'requirements': ['thermal', 'bag'],
                'delay': {'since_lookup': 0, 'since_due': -100500},
            },
        ],
    )

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    delayed_claim_uuid_1, _ = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(seconds=1000),
        taxi_class='courier',
    )
    _insert_claim_estimation(
        cursor, delayed_claim_uuid_1, ['courier', 'express'],
    )
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['claims'][0] == {
        'claim_id': matching.AnyString(),
        'allowed_classes': ['courier'],
        'ignorable_special_requirements': [],
    }


async def test_client_requirements(
        taxi_cargo_claims, pgsql, claims_exp_extended_tariffs,
):
    await claims_exp_extended_tariffs(delayed_classes=['express'])

    cursor = pgsql['cargo_claims'].cursor()
    # Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    soon_claim_uuid, soon_uuid = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
        taxi_classes=['courier', 'eda', 'lavka'],
    )
    _insert_claim_estimation(cursor, soon_claim_uuid, ['courier', 'express'])
    # Invalidate cache
    await taxi_cargo_claims.invalidate_caches()
    # Check handler response
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = {
        c['claim_id']: set(c.get('allowed_classes'))
        for c in response.json()['claims']
    }
    assert response_claims == {soon_uuid: {'courier', 'eda', 'lavka'}}


@pytest.mark.config(
    CARGO_CANDIDATES_ACTIVE_CLAIMS_CACHE_SETTINGS=_build_settings(
        response_chunk_size=2,
    ),
)
async def test_active_claims_cursor(
        taxi_cargo_claims, claims_exp_extended_tariffs, pgsql,
):
    await claims_exp_extended_tariffs()

    # Fill cache
    cursor = pgsql['cargo_claims'].cursor()
    #  Add claims
    now = datetime.datetime.now(datetime.timezone.utc)
    _, soon_1 = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    _, soon_2 = _insert_claim(
        cursor,
        'performer_lookup',
        False,
        now - datetime.timedelta(minutes=1),
        None,
    )
    _, delayed_1 = _insert_claim(
        cursor,
        'performer_lookup',
        True,
        now - datetime.timedelta(days=1),
        now + datetime.timedelta(minutes=5),
    )
    # update cache
    await taxi_cargo_claims.invalidate_caches()

    expected_claim_ids = sorted([soon_1, soon_2, delayed_1])

    # Check only first two records returned
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    response_claims = _get_claim_ids(response)
    assert response_claims == set(expected_claim_ids[0:2])

    # Check cursor returned
    assert 'cursor' in response.json()

    # Check last record returned
    response = await taxi_cargo_claims.get(
        '/v1/claims/list/performer-lookup',
        params={'cursor': response.json()['cursor']},
    )
    assert response.status_code == 200
    response_claims = _get_claim_ids(response)
    assert response_claims == set(expected_claim_ids[2:])


@pytest.mark.config(
    CARGO_CANDIDATES_ACTIVE_CLAIMS_CACHE_SETTINGS=_build_settings(
        response_chunk_throttling_ms=100,
    ),
)
async def test_candidates_throttling(taxi_cargo_claims):
    response = await taxi_cargo_claims.get('/v1/claims/list/performer-lookup')
    assert response.status_code == 200
    assert response.headers['X-Polling-Delay-Ms'] == '100'
