import pytest

# Common constants:

PG_DBNAME = 'eats_logistics_performer_payouts'
PG_FILES = ['eats_logistics_performer_payouts/insert_all_factors.sql']


# Time helpers:

TIME_TEMPLATE = '2020-06-30T{:0>2d}:{:0>2d}:00+{:0>2d}:00'


def mk_time_msk(daytime_msk):
    hour_msk, minute_msk = [int(c) for c in daytime_msk.split(':')]
    return TIME_TEMPLATE.format(hour_msk, minute_msk, 3)


def mk_time_utc(daytime_msk):
    hour_msk, minute_msk = [int(c) for c in daytime_msk.split(':')]
    return TIME_TEMPLATE.format(hour_msk - 3, minute_msk, 0)


# Factor helpers:


def mk_factor_str(name, value):
    factor_string = {'name': name, 'type': 'string', 'value': value}
    return factor_string


def mk_factor_dtm(name, value):
    factor_datetime = {'name': name, 'type': 'datetime', 'value': value}
    return factor_datetime


def mk_factor_int(name, value):
    factor_int = {'name': name, 'type': 'int', 'value': value}
    return factor_int


def mk_factor_dec(name, value):
    factor_int = {'name': name, 'type': 'decimal', 'value': value}
    return factor_int


# Shift helpers:


def parse_times(planned_times, actual_times, mk_time):
    planned_start_at = None
    planned_end_at = None
    actual_start_at = None
    actual_end_at = None
    if planned_times is not None:
        planned_start_at = mk_time(planned_times[0])
        planned_end_at = mk_time(planned_times[1])
    if actual_times is not None:
        actual_start_at = mk_time(actual_times[0])
        if len(actual_times) > 1:
            actual_end_at = mk_time(actual_times[1])
    return [planned_start_at, planned_end_at, actual_start_at, actual_end_at]


DFT_SHIFT_TYPE = 'planned'
DFT_TRAVEL_TYPE = 'bicycle'
DFT_EATS_REGION_ID = '3'
DFT_PERFORMER_ID = '1'
DFT_COURIER_ID = '0023_A6FE'
DFT_POST = 'courier'


class Shift:
    def __init__(
            self,
            shift_id,
            status,
            shift_type=DFT_SHIFT_TYPE,
            travel_type=DFT_TRAVEL_TYPE,
            eats_region_id=DFT_EATS_REGION_ID,
            performer_id=DFT_PERFORMER_ID,
            courier_id=DFT_COURIER_ID,
            plan=None,
            work=None,
            duration=None,
            offline_time=None,
            guarantee=None,
            pause_duration=None,
            is_newbie=None,
            post=DFT_POST,
    ):
        self.data = {
            'shift_id': shift_id,
            'courier_id': courier_id,
            'eats_id': performer_id,
            'region_id': int(eats_region_id),
            'status': status,
            'type': shift_type,
            'pool': post,
            'travel_type': travel_type,
        }
        self.stq = {
            'shift_id': shift_id,
            'courier_id': courier_id,
            'eats_id': performer_id,
            'region_id': int(eats_region_id),
            'status': status,
            'type': shift_type,
            'pool': post,
            'travel_type': travel_type,
        }
        self.subject = {
            'id': {'id': shift_id, 'type': 'shift'},
            'relations': [{'id': performer_id, 'type': 'performer'}],
            'factors': [],
        }

        ps_msk, pe_msk, as_msk, ae_msk = parse_times(plan, work, mk_time_msk)
        ps_utc, pe_utc, as_utc, ae_utc = parse_times(plan, work, mk_time_utc)

        # Order of factors is important
        factors = [
            mk_factor_str('travel_type', travel_type),
            mk_factor_str('eats_region_id', eats_region_id),
            mk_factor_str('type', shift_type),
            mk_factor_str('status', status),
            mk_factor_str('post', post),
        ]

        if ps_utc is not None:
            self.data['planned_to_start_at'] = ps_msk
            self.stq['planned_to_start_at'] = ps_utc
            factors.append(mk_factor_dtm('planned_start_at', ps_utc))

        if as_utc is not None:
            self.data['started_at'] = as_msk
            self.stq['started_at'] = as_utc
            factors.append(mk_factor_dtm('actual_start_at', as_utc))

        if pe_utc is not None:
            self.data['planned_to_close_at'] = pe_msk
            self.stq['planned_to_close_at'] = pe_utc
            factors.append(mk_factor_dtm('planned_end_at', pe_utc))

        if ae_utc is not None:
            self.data['closes_at'] = ae_msk
            self.stq['closes_at'] = ae_utc
            factors.append(mk_factor_dtm('actual_end_at', ae_utc))

        if duration is not None:
            self.data['duration'] = duration
            self.stq['duration'] = duration
            factors.append(mk_factor_int('duration', duration))

        if offline_time is not None:
            self.data['offline_time'] = offline_time
            self.stq['offline_time'] = offline_time
            factors.append(mk_factor_int('offline_time', offline_time))

        if guarantee is not None:
            self.data['guarantee'] = guarantee
            self.stq['guarantee'] = guarantee
            factors.append(mk_factor_dec('guarantee', guarantee))

        if pause_duration is not None:
            self.data['pause_duration'] = pause_duration
            self.stq['pause_duration'] = pause_duration
            factors.append(mk_factor_int('pause_duration', pause_duration))

        if is_newbie is not None:
            self.data['is_newbie'] = is_newbie
            self.stq['is_newbie'] = is_newbie
            factors.append(mk_factor_int('is_newbie', is_newbie))

        # Finish filling the .subject
        self.subject['factors'] = factors
        if (status == 'closed') and (ae_utc is not None):
            self.subject['time_point_at'] = ae_utc

        # And also fill the 'driver_profile' subject
        self.dprofile_subject = {
            'id': {'id': courier_id, 'type': 'driver_profile'},
            'relations': [{'id': performer_id, 'type': 'performer'}],
        }


# courier shifts:

# Set 0:

SHIFT_06 = Shift('06', 'not_started', plan=['10:00', '17:00'])

SHIFT_07 = Shift(
    '07',
    'closed',
    shift_type='unplanned',
    work=['11:00', '13:00'],
    duration=7200,
)

SHIFT_08 = Shift(
    '08',
    'closed',
    plan=['14:00', '18:00'],
    work=['14:00', '18:00'],
    duration=14400,
)

# Set 1:

SHIFT_10 = Shift('10', 'not_started', plan=['10:00', '15:00'])
SHIFT_11 = Shift('11', 'not_started', plan=['10:15', '15:00'])
SHIFT_12 = Shift(
    '12',
    'closed',
    plan=['10:30', '15:00'],
    work=['10:30', '14:55'],
    duration=8700,
    pause_duration=0,
    offline_time=300,
    guarantee='500.99',
)

# Set 2:

SHIFT_20 = Shift(
    '20',
    'closed',
    plan=['10:00', '14:00'],
    work=['10:00', '14:12'],
    duration=7920,
    pause_duration=0,
    offline_time=0,
    guarantee='519.85',
)

SHIFT_21 = Shift(
    '21',
    'closed',
    plan=['14:00', '16:00'],
    work=['14:12', '16:00'],
    duration=6480,
    pause_duration=0,
    offline_time=720,
    guarantee='480.15',
)


# Tests:

# [no intersections] - handle single not started planned shift. The whole
# planned interval makes missed time.
# [planned x unplanned] - intersection of planned not started with an
# unplanned closed.
# [chain] - a chain of shifts, intersecting with each other.
# [stack] - most common case - when courier is more, than 15min late to the
# planned slot, it becomes 'not started' and another planned slot is created
# automatically.
# [benign chain] - when a courier worked perfectly, and he got late to the
# second shift only because he was delivering order from the first one.
@pytest.mark.pgsql(PG_DBNAME, files=PG_FILES)
@pytest.mark.parametrize(
    'shift,intersections,missed_times',
    [
        pytest.param(SHIFT_06, {}, {'06': 420}, id='no intersections'),
        pytest.param(
            SHIFT_06,
            {'06': [SHIFT_07.data]},
            {'06': 300},
            id='planned x unplanned',
        ),
        pytest.param(
            SHIFT_06,
            {'06': [SHIFT_07.data, SHIFT_08.data], '08': [SHIFT_06.data]},
            {'06': 120, '08': 0},
            id='chain',
        ),
        pytest.param(
            SHIFT_10,
            {
                '10': [SHIFT_11.data, SHIFT_12.data],
                '11': [SHIFT_10.data, SHIFT_12.data],
                '12': [SHIFT_10.data, SHIFT_11.data],
            },
            {'10': 35, '11': 0, '12': 0},
            id='stack',
        ),
        pytest.param(
            SHIFT_21,
            {'20': [SHIFT_21.data], '21': [SHIFT_20.data]},
            {'20': 0, '21': 0},
            id='benign chain',
        ),
    ],
)
async def test_shift_processing(
        intersections, missed_times, shift, stq_runner, testpoint,
):
    @testpoint('test_subject_request')
    def check_subject(subject):
        # Allow exceptions
        subject_type = subject['id']['type']
        if subject_type == 'shift':
            factors = subject['factors']
            if len(factors) == 1:
                if factors[0]['name'] == 'missed_time':
                    # There is a separate testpoint on 'missed time',
                    # it shall not be checked as a subject
                    return

            assert subject == shift.subject
        elif subject_type == 'driver_profile':
            assert subject == shift.dprofile_subject

    await stq_runner.eats_logistics_performer_payouts_process_shift.call(
        task_id='test', kwargs={'shift_data': shift.stq},
    )

    assert check_subject.times_called == 2


@pytest.mark.pgsql(PG_DBNAME, files=['insert_subjects_and_factors.sql'])
@pytest.mark.parametrize(
    'shift,finish_times_called,continue_times_called',
    [
        pytest.param(
            Shift('1', 'not_started', plan=['10:00', '17:00']),
            1,
            0,
            id='not_started_in_db',
        ),
        pytest.param(
            Shift('2', 'closed', plan=['10:00', '17:00']),
            1,
            0,
            id='closed_in_db',
        ),
    ],
)
async def test_shift_terminal_status_has_not_started_twice(
        stq_runner,
        testpoint,
        shift,
        finish_times_called,
        continue_times_called,
):
    @testpoint('finish_task_after_status_check')
    def test_finish_stq_task_after_check_status(req):
        pass

    @testpoint('continue_task_after_status_check')
    def test_continue_stq_task_after_check_status(req):
        pass

    await stq_runner.eats_logistics_performer_payouts_process_shift.call(
        task_id='test', kwargs={'shift_data': shift.stq},
    )

    assert (
        test_finish_stq_task_after_check_status.times_called
        == finish_times_called
    )
    assert (
        test_continue_stq_task_after_check_status.times_called
        == continue_times_called
    )
