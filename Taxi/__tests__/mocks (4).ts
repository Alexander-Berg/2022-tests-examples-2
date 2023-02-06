import moment from 'moment-timezone';

import {FIELD_PERIOD_IS_INCORRECT} from 'api/shiftsStats/consts';
import {convertLoadParamsForRequest} from 'api/shiftsStats/converters';
import {ConvertersTestDataType} from 'types/tests';

type CorrectMockType = ConvertersTestDataType<typeof convertLoadParamsForRequest>;

export const PERFECT_MOCK_FOR_LOAD: CorrectMockType = {
    payload: [{
        period: [
            moment('2021-12-14T13:00:00+03:00'),
            moment('2021-12-16T10:00:00+03:00'),
        ],
        measure: 'man_hours',
        skill: 'lavka',
        step_minutes: 60,
    }],
    result: {
        datetime_from: '2021-12-14T00:00:00+03:00',
        datetime_to: '2021-12-17T00:00:00+03:00',
        measure: 'man_hours',
        skill: 'lavka',
        step_minutes: 60,
    },
};

export const ANOTHER_PERFECT_MOCK_FOR_LOAD: CorrectMockType = {
    payload: [{
        period: [
            moment('2021-12-14T13:00:00+03:00'),
            moment('2021-12-16T10:00:00+03:00'),
        ],
        measure: 'man_hours',
        skill: 'lavka',
        step_minutes: 60,
    }],
    result: {
        datetime_from: '2021-12-14T00:00:00+03:00',
        datetime_to: '2021-12-17T00:00:00+03:00',
        measure: 'man_hours',
        skill: 'lavka',
        step_minutes: 60,
    },
};

export const MOCK_WITHOUT_STEP_MINUTES_FOR_LOAD: CorrectMockType = {
    payload: [{
        period: [
            moment('2021-12-14T13:00:00+03:00'),
            moment('2021-12-16T10:00:00+03:00'),
        ],
        measure: 'man_hours',
        skill: 'lavka',
    }],
    result: {
        datetime_from: '2021-12-14T00:00:00+03:00',
        datetime_to: '2021-12-17T00:00:00+03:00',
        measure: 'man_hours',
        skill: 'lavka',
    },
};

export const MOCK_WITHOUT_SECOND_PERIOD_FOR_LOAD: CorrectMockType = {
    payload: [{
        period: [
            moment('2021-12-11T03:00:00+03:00'),
            undefined,
        ],
        measure: 'man_hours',
        skill: 'lavka',
        step_minutes: 60,
    }],
    result: {
        datetime_from: '2021-12-14T00:00:00+03:00',
        datetime_to: '',
        measure: 'man_hours',
        skill: 'lavka',
        step_minutes: 60,
    },
    error: FIELD_PERIOD_IS_INCORRECT,
};

export const MOCK_WITHOUT_PERIODS_FOR_LOAD: CorrectMockType = {
    payload: [{
        period: [undefined, undefined],
        measure: 'man_hours',
        skill: 'lavka',
        step_minutes: 60,
    }],
    result: {
        datetime_from: '',
        datetime_to: '',
        measure: 'man_hours',
        skill: 'lavka',
        step_minutes: 60,
    },
    error: FIELD_PERIOD_IS_INCORRECT,
};

export const MOCK_WITHOUT_PERIOD_FOR_LOAD: CorrectMockType = {
    payload: [{
        period: undefined,
        measure: 'man_count',
        skill: 'test',
        step_minutes: 15,
    }],
    result: {
        datetime_from: '',
        datetime_to: '',
        measure: 'man_hours',
        skill: 'lavka',
        step_minutes: 60,
    },
    error: FIELD_PERIOD_IS_INCORRECT,
};
