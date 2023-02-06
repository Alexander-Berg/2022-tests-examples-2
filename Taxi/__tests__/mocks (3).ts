import moment from 'moment-timezone';

import {CustomRecord} from 'components/ShiftSidebar/sagas/shift/request/types';
import {Operator} from 'types/api/backend-py3/definitions';
import {EditShiftsFormType} from 'types/shifts';
import {ConvertersTestDataType} from 'types/tests';

import {
    filtersFromClientToServer,
    prepareDisciplineFiltersToRequest,
    prepareChartFiltersToRequest,
    convertBreaks,
    prepareOperatorsShift,
    convertProjectActivityToServer,
    prepareShiftForSaveRequest,
    convertTableShiftToServerShift,
    convertPeriodForRequest,
    normalizeShiftsPayload,
} from '../converters';

export const FILTERS_CLIENT_TO_SERVER_MOCK: ConvertersTestDataType<typeof filtersFromClientToServer> = {
    payload: [{
        skill: 'lavka',
        supervisors: [],
        period: [
            moment('2021-11-30T21:00:00.000Z'),
            moment('2021-12-08T21:00:00.000Z'),
        ],
        multiskill: false,
        limit: 10,
        offset: 0,
        shift_filter: {
            shift_events: [],
            period_filter: {
                datetime_from: '2021-12-01T00:00:00+03:00',
                datetime_to: '2021-12-09T00:00:00+03:00',
                period_filter_type: 'expires',
            },
        },
        tag_filter: {
            connection_policy: 'disjunction',
            ownership_policy: 'include',
            tags: [
                'tag4',
                'tag5',
            ],
        },
    }],
    result: {
        multiskill: false,
        skill: 'lavka',
        datetime_from: '2021-11-30T23:59:00+03:00',
        datetime_to: '2021-12-09T00:00:00+03:00',
        shift_filter: {
            shift_events: [],
            period_filter: {
                datetime_from: '2021-12-01T00:00:00+03:00',
                datetime_to: '2021-12-09T00:00:00+03:00',
                period_filter_type: 'expires',
            },
        },
        limit: 10,
        offset: 0,
        tag_filter: {
            connection_policy: 'disjunction',
            ownership_policy: 'include',
            tags: [
                'tag4',
                'tag5',
            ],
        },
        supervisors: undefined,
    },
};

export const PREPARE_CHART_FILTERS_MOCK: ConvertersTestDataType<typeof prepareChartFiltersToRequest> = {
    payload: [
        {
            period: [
                moment('2021-11-30T21:00:00.000Z'),
                moment('2021-12-08T20:59:00.000Z'),
            ],
            skill: 'lavka',
            violations: ['absent'],
            limit: 50,
            offset: 0,
            tag_filter: {
                connection_policy: 'disjunction',
                ownership_policy: 'include',
                tags: ['tag3', 'tag4'],
            },
            state: 'ready',
            isViolationsVisible: true,
        },
    ],
    result: {
        skill: 'lavka',
        limit: 50,
        offset: 0,
        state: 'ready',
        datetime_from: '2021-12-01T00:00:00+03:00',
        datetime_to: '2021-12-09T00:00:00+03:00',
        tag_filter: {
            connection_policy: 'disjunction',
            ownership_policy: 'include',
            tags: ['tag3', 'tag4'],
        },
        shift_violation_filter: {
            shift_violation_types: ['absent'],
        },
        load_entities: ['shifts', 'shift_breaks', 'shift_events', 'absences', 'shift_violations'],
        yandex_uids: undefined,
        supervisors: undefined,
        absence_type_ids: undefined,
        full_name: undefined,
    },
};

export const PREPARE_DISCIPLINE_FILTERS_MOCK: ConvertersTestDataType<typeof prepareDisciplineFiltersToRequest> = {
    payload: [{
        period: [
            moment('2021-12-21T06:00:00.000Z'),
            moment('2021-12-21T17:59:59.000Z'),
        ],
        skill: ['lavka'],
        violations: ['absent'],
        focusPeriod: [
            moment('2021-12-21T06:00:00.000Z'),
            moment('2021-12-21T17:59:59.000Z'),
        ],
        limit: 500,
        offset: 0,
    }],
    result: {
        skill: 'lavka',
        datetime_from: '2021-12-21T09:00:00+03:00',
        datetime_to: '2021-12-21T20:59:59+03:00',
        limit: 500,
        offset: 0,
        shift_violation_filter: {
            datetime_from: '2021-12-21T09:00:00+03:00',
            datetime_to: '2021-12-21T20:59:59+03:00',
            shift_violation_types: ['absent'],
        },
        full_name: undefined,
        yandex_uids: undefined,
    },
};

export const CONVERT_BREAKS_MOCK: ConvertersTestDataType<typeof convertBreaks> = {
    payload: [{
        period_start: moment('2021-12-01T21:00:00.000Z'),
        period_end: moment('2021-12-02T09:00:00.000Z'),
        breaks: [{
            period: [undefined, undefined],
            type: 'lunchtime',
            start: moment('2021-12-02T01:00:00.000Z'),
            duration_minutes: 60,
        }],
        operators: ['1130000003753880'],
        spread_breaks: false,
        duration: moment('2021-12-02T09:00:00.000Z'),
    }],
    result: [{
        type: 'lunchtime',
        start: '2021-12-02T04:00:00+03:00',
        duration_minutes: 60,
        id: undefined,
    }],
};

const SELECTED_SHIFT_MOCK: CustomRecord = {
    operator: {
        yandex_uid: '1130000003232146',
        revision_id: '2021-12-22T06:55:12.057990 +0000',
        callcenter_id: 'callcenter_id_1',
        login: 'aa@taxi.auto.connect-test.tk',
        state: 'ready',
        skills: ['lavka'],
        tags: [],
        employment_date: '2020-09-02',
        full_name: 'aa bb cc',
        schedules: [{
            record_id: 345,
            starts_at: '2020-12-07T00:00:00+03:00',
            schedule_type_info: {schedule_type_id: 64},
            revision_id: '2021-03-23T13:36:23.434626 +0000',
            skills: ['lavka'],
            audit: {updated_at: '2021-03-23T16:36:23.434626+03:00'},
        }],
    },
    shifts: [
        {
            start: '2021-12-02T21:00:00+03:00',
            duration_minutes: 705,
            skill: 'lavka',
            shift_id: 73884,
            operators_schedule_types_id: 345,
            frozen: false,
            type: 'common',
            breaks: [
                {
                    start: '2021-12-02T23:00:00+03:00',
                    duration_minutes: 15,
                    id: 150524,
                    type: 'technical',
                },
                {
                    start: '2021-12-03T01:30:00+03:00',
                    duration_minutes: 15,
                    id: 150525,
                    type: 'technical',
                },
                {
                    start: '2021-12-03T03:00:00+03:00',
                    duration_minutes: 15,
                    id: 150526,
                    type: 'technical',
                },
                {
                    start: '2021-12-03T04:45:00+03:00',
                    duration_minutes: 30,
                    id: 150527,
                    type: 'lunchtime',
                },
                {
                    start: '2021-12-03T05:45:00+03:00',
                    duration_minutes: 15,
                    id: 150528,
                    type: 'technical',
                },
            ],
            shift_violations: [
                {
                    id: 4940,
                    type: 'absent',
                    start: '2021-12-02T21:00:00+03:00',
                    duration_minutes: 705,
                    shift_id: 73884,
                },
            ],
        },
    ],
    absences: [],
    actual_shifts: [],
    shift_drafts: [],
    shift: {
        start: '2021-12-02T21:00:00+03:00',
        duration_minutes: 705,
        skill: 'lavka',
        shift_id: 73884,
        operators_schedule_types_id: 345,
        frozen: false,
        type: 'common',
        breaks: [
            {
                start: '2021-12-02T23:00:00+03:00',
                duration_minutes: 15,
                id: 150524,
                type: 'technical',
            },
            {
                start: '2021-12-03T01:30:00+03:00',
                duration_minutes: 15,
                id: 150525,
                type: 'technical',
            },
            {
                start: '2021-12-03T03:00:00+03:00',
                duration_minutes: 15,
                id: 150526,
                type: 'technical',
            },
            {
                start: '2021-12-03T04:45:00+03:00',
                duration_minutes: 30,
                id: 150527,
                type: 'lunchtime',
            },
            {
                start: '2021-12-03T05:45:00+03:00',
                duration_minutes: 15,
                id: 150528,
                type: 'technical',
            },
        ],
        shift_violations: [
            {
                id: 4940,
                type: 'absent',
                start: '2021-12-02T21:00:00+03:00',
                duration_minutes: 705,
                shift_id: 73884,
            },
        ],
        audit: {
            updated_at: '2021-12-03T08:45:04.363654+03:00',
            author_yandex_uid: 'shift_violations_periodic_job',
        },
    },
};

export const EDIT_SHIFT_FORM_MOCK: EditShiftsFormType = {
    period_handler: 'custom',
    period_start: moment('2021-12-02T18:00:00.000Z'),
    period_end: moment('2021-12-03T06:45:00.000Z'),
    is_additional: false,
    project_activities: [],
    breaks: [
        {
            start: moment('2021-12-02T20:00:00.000Z'),
            duration_minutes: 15,
            id: 150524,
            type: 'technical',
        },
        {
            start: moment('2021-12-02T22:30:00.000Z'),
            duration_minutes: 15,
            id: 150525,
            type: 'technical',
        },
        {
            start: moment('2021-12-03T00:00:00.000Z'),
            duration_minutes: 15,
            id: 150526,
            type: 'technical',
        },
        {
            start: moment('2021-12-03T01:45:00.000Z'),
            duration_minutes: 30,
            id: 150527,
            type: 'lunchtime',
        },
        {
            start: moment('2021-12-03T02:45:00.000Z'),
            duration_minutes: 15,
            id: 150528,
            type: 'technical',
        },
    ],
    operators: ['1130000003232146'],
    spread_breaks: false,
    duration: moment('2021-12-22T09:45:00.000Z'),
    shift_id: 73884,
    yandex_uid: '1130000003232146',
    skill: 'lavka',
    revision_id: '2021-12-22T06:55:12.057990 +0000',
    type: 'common',
    frozen: false,
    shift_violations: [
        {
            id: 4940,
            type: 'absent',
            start: '2021-12-02T18:00:00.000Z',
            duration_minutes: 705,
            shift_id: 73884,
        },
    ],
    audit: {
        updated_at: '2021-12-03T08:45:04.363654+03:00',
        author_yandex_uid: 'shift_violations_periodic_job',
    },
};
const OPERATOR_MOCK: Operator = {
    yandex_uid: '1130000003232146',
    login: 'aa@taxi.auto.connect-test.tk',
    full_name: 'aa bb cc',
    callcenter_id: 'callcenter_id_1',
    state: 'ready',
    role_in_telephony: 'ru_support_team_leader',
    employment_date: '2020-09-02',
    revision_id: '2021-12-22T06:55:12.057990 +0000',
    skills: ['lavka'],
    schedules: [
        {
            record_id: 345,
            starts_at: '2020-12-07T00:00:00+03:00',
            schedule_type_info: {
                schedule_type_id: 64,
                revision_id: '2021-08-12T10:37:57.675859 +0000',
                schedule_alias: '21-08:45 / 1*2',
                schedule: [1, 2],
                first_weekend: false,
                start: '18:00:00',
                duration_minutes: 705,
            },
            revision_id: '2021-03-23T13:36:23.434626 +0000',
            skills: ['lavka'],
            audit: {updated_at: '2021-03-23T16:36:23.434626+03:00'},
        },
    ],
    roles: [],
};

export const PREPARE_OPERATORS_SHIFT_MOCK: ConvertersTestDataType<typeof prepareOperatorsShift> = {
    payload: [SELECTED_SHIFT_MOCK, EDIT_SHIFT_FORM_MOCK, OPERATOR_MOCK],
    result: {
        yandex_uid: '1130000003232146',
        full_name: 'aa bb cc',
        skills: ['lavka'],
        shift_id: 73884,
        segments: [],
        type: 'common',
        schedules: [
            {
                record_id: 345,
                starts_at: '2020-12-07T00:00:00+03:00',
                schedule_type_info: {
                    schedule_type_id: 64,
                    revision_id: '2021-08-12T10:37:57.675859 +0000',
                    schedule_alias: '21-08:45 / 1*2',
                    schedule: [1, 2],
                    first_weekend: false,
                    start: '18:00:00',
                    duration_minutes: 705,
                },
                revision_id: '2021-03-23T13:36:23.434626 +0000',
                skills: ['lavka'],
                audit: {updated_at: '2021-03-23T16:36:23.434626+03:00'},
            },
        ],
        revision_id: '2021-12-22T06:55:12.057990 +0000',
        events: undefined,
        breaks: SELECTED_SHIFT_MOCK.shift.breaks,
    },
};

export const CONVERT_PA_TO_SERVER_MOCK: ConvertersTestDataType<typeof convertProjectActivityToServer> = {
    payload: [{
        period: [
            moment('2021-11-30T21:00:00.000Z'),
            moment('2021-12-01T03:00:00.000Z'),
        ],
        event_id: 47,
        description: 'Test',
    }],
    result: {
        id: undefined,
        event_id: 47,
        start: '2021-12-01T00:00:00+03:00',
        duration_minutes: 360,
        description: 'Test',
    },
};

export const PREPARE_SHIFT_FOR_SAVE_MOCK: ConvertersTestDataType<typeof prepareShiftForSaveRequest> = {
    payload: [SELECTED_SHIFT_MOCK, {
        ...EDIT_SHIFT_FORM_MOCK,
        duration: moment().set('h', 12).set('minute', 45),
    }, OPERATOR_MOCK],
    result: {
        start: '2021-12-02T21:00:00+03:00',
        skill: 'lavka',
        duration_minutes: 765,
        operators: [
            {
                yandex_uid: '1130000003232146',
                full_name: 'aa bb cc',
                skills: ['lavka'],
                schedules: PREPARE_OPERATORS_SHIFT_MOCK.result.schedules,
                revision_id: '2021-12-22T06:55:12.057990 +0000',
                events: [],
                breaks: SELECTED_SHIFT_MOCK.shift.breaks,
                shift_id: 73884,
                type: 'common',
                segments: [],
            },
        ],
    },
};

export const CONVERT_TABLE_SHIFT_TO_SERVER_MOCK: ConvertersTestDataType<typeof convertTableShiftToServerShift> = {
    payload: [{
        shift_id: 73948,
        yandex_uid: '1130000003228464',
        revision_id: '2021-12-22T11:13:41.465894 +0000',
        skills: ['lavka'],
        skill: 'lavka',
        type: 'additional',
        full_name: 'test hanged',
        duration_minutes: 360,
        phone: '+1',
        frozen: false,
        period_margins: [
            moment('2021-12-02T21:00:00.000Z'),
            moment('2021-12-03T03:00:00.000Z'),
        ],
        is_additional: true,
        description: 'violation',
        period: '',
        starts_at: '2020-12-11T00:00:00+03:00',
        breaks: [
            {
                id: 150732,
                type: 'technical',
                start: moment('2021-12-02T23:45:00.000Z'),
                duration_minutes: 15,
            },
            {
                id: 150733,
                type: 'lunchtime',
                start: moment('2021-12-03T00:30:00.000Z'),
                duration_minutes: 45,
            },
        ],
        project_activities: [],
        violation: [
            {
                id: 4923,
                type: 'absent',
                start: '2021-12-02T00:00:00+03:00',
                duration_minutes: 360,
                shift_id: 73948,
            },
        ],
        segments: [
            {
                skill: 'lavka',
                start: '2021-12-02T01:00:00+03:00',
                duration_minutes: 30,
                id: 1,
            },
            {
                skill: 'lavka',
                start: '2021-12-02T02:30:00+03:00',
                duration_minutes: 15,
                id: 2,
            },
        ],
        operator: {
            login: 'aa@taxi.auto.connect-test.tk',
            yandex_uid: '1130000003232146',
            full_name: 'aa bb cc',
            skills: ['lavka'],
            schedules: PREPARE_OPERATORS_SHIFT_MOCK.result.schedules,
            revision_id: '2021-12-22T06:55:12.057990 +0000',
        },
    }],
    result: {
        start: '2021-12-03T00:00:00+03:00',
        skill: undefined,
        duration_minutes: 360,
        operators: [
            {
                yandex_uid: '1130000003228464',
                revision_id: '2021-12-22T11:13:41.465894 +0000',
                full_name: 'test hanged',
                shift_id: 73948,
                phone: '+1',
                skills: ['lavka'],
                events: [],
                breaks: [
                    {
                        id: 150732,
                        type: 'technical',
                        start: '2021-12-03T02:45:00+03:00',
                        duration_minutes: 15,
                    },
                    {
                        id: 150733,
                        type: 'lunchtime',
                        start: '2021-12-03T03:30:00+03:00',
                        duration_minutes: 45,
                    },
                ],
                type: 'additional',
                segments: [
                    {
                        skill: 'lavka',
                        start: '2021-12-03T01:00:00+03:00',
                        duration_minutes: 30,
                        id: 1,
                    },
                    {
                        skill: 'lavka',
                        start: '2021-12-03T02:30:00+03:00',
                        duration_minutes: 15,
                        id: 2,
                    },
                ],
            },
        ],
    },
};

export const CONVERT_PERIOD_FOR_REQUEST_MOCK: ConvertersTestDataType<typeof convertPeriodForRequest> = {
    payload: [[moment().startOf('day'), moment().startOf('day').add(3, 'h')]],
    result: {
        datetime_from: moment().startOf('day').format(),
        datetime_to: moment().startOf('day').add(3, 'h').format(),
    },
};

export const NORMALIZE_SHIFTS_PAYLOAD_MOCK: ConvertersTestDataType<typeof normalizeShiftsPayload> = {
    payload: [{
        skill: 'lavka',
        limit: 50,
        offset: 0,
        state: 'ready',
        datetime_from: '2021-12-01T00:00:00+03:00',
        datetime_to: '2021-12-09T00:00:00+03:00',
        load_entities: [
            'shifts',
            'shift_breaks',
            'shift_events',
            'absences',
            'shift_violations',
        ],
        sort_by_interval: {
            sequence: ['shift_starts'],
            datetime_from: '2021-12-01T00:00:00+03:00',
            datetime_to: '2021-12-02T00:00:00+03:00',
        },
        full_name: '',
        login: '',
        supervisors: [],
        yandex_uids: '',
    }],
    result: {
        skill: 'lavka',
        limit: 50,
        offset: 0,
        state: 'ready',
        datetime_from: '2021-12-01T00:00:00+03:00',
        datetime_to: '2021-12-09T00:00:00+03:00',
        load_entities: [
            'shifts',
            'shift_breaks',
            'shift_events',
            'absences',
            'shift_violations',
        ],
        sort_by_interval: {
            sequence: [
                'shift_starts',
            ],
            datetime_from: '2021-12-01T00:00:00+03:00',
            datetime_to: '2021-12-02T00:00:00+03:00',
        },
        full_name: undefined,
        login: undefined,
        supervisors: undefined,
        yandex_uids: undefined,
    },
};
