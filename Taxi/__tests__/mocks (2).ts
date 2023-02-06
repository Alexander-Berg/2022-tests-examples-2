import moment from 'moment-timezone';

import {convertProjectActivitiesFromRawToForm} from 'api/projectActivities/converters';
import {ConvertersTestDataType} from 'types/tests';

type CorrectedMockType = ConvertersTestDataType<typeof convertProjectActivitiesFromRawToForm>;

moment.locale('en');
moment.tz.setDefault('UTC');
export const PA_FROM_RAW_TO_FORM_PERFECT_MOCK_FOR_UTC: CorrectedMockType = {
    payload: [
        [
            {
                id: 674,
                event_id: 8,
                start: '2021-12-16T00:00:00.000Z',
                duration_minutes: 410,
                description: 'mvam',
            },
            {
                id: 123,
                event_id: 7,
                start: '2021-12-15T06:00:00.000Z',
                duration_minutes: 120,
            },
            {
                event_id: 7,
                start: '2021-12-10T08:00:00.000Z',
                duration_minutes: 153,
            },
        ],
        {
            7: 'Training with breaks',
            8: 'OKK',
        },
    ],
    result: [
        {
            id: 674,
            event_id: 8,
            event_name: 'OKK',
            period: [
                moment('2021-12-16T00:00:00.000Z'),
                moment('2021-12-16T00:00:00.000Z').clone().add(410, 'minutes'),
            ],
            period_formatted: '16.12(Thu) 00:00 - 16.12(Thu) 06:50',
            description: 'mvam',
        },
        {
            id: 123,
            event_id: 7,
            event_name: 'Training with breaks',
            period: [
                moment('2021-12-15T06:00:00.000Z'),
                moment('2021-12-15T06:00:00.000Z').clone().add(120, 'minutes'),
            ],
            period_formatted: '15.12(Wed) 06:00 - 15.12(Wed) 08:00',
        },
        {
            event_id: 7,
            event_name: 'Training with breaks',
            period: [
                moment('2021-12-10T08:00:00.000Z'),
                moment('2021-12-10T08:00:00.000Z').clone().add(153, 'minutes'),
            ],
            period_formatted: '10.12(Fri) 08:00 - 10.12(Fri) 10:33',
        },
    ],
};

moment.tz.setDefault('Europe/Samara');
export const PA_FROM_RAW_TO_FORM_PERFECT_MOCK_FOR_SAMARA: CorrectedMockType = {
    payload: [
        [
            {
                id: 674,
                event_id: 8,
                start: '2021-12-16T00:00:00.000Z',
                duration_minutes: 410,
                description: 'mvam',
            },
            {
                id: 123,
                event_id: 7,
                start: '2021-12-15T06:00:00.000Z',
                duration_minutes: 120,
            },
            {
                event_id: 7,
                start: '2021-12-10T08:00:00.000Z',
                duration_minutes: 153,
            },
        ],
        {
            7: 'Training with breaks',
            8: 'OKK',
        },
    ],
    result: [
        {
            id: 674,
            event_id: 8,
            event_name: 'OKK',
            period: [
                moment('2021-12-16T00:00:00.000Z'),
                moment('2021-12-16T00:00:00.000Z').clone().add(410, 'minutes'),
            ],
            period_formatted: '16.12(Thu) 04:00 - 16.12(Thu) 10:50',
            description: 'mvam',
        },
        {
            id: 123,
            event_id: 7,
            event_name: 'Training with breaks',
            period: [
                moment('2021-12-15T06:00:00.000Z'),
                moment('2021-12-15T06:00:00.000Z').clone().add(120, 'minutes'),
            ],
            period_formatted: '15.12(Wed) 10:00 - 15.12(Wed) 12:00',
        },
        {
            event_id: 7,
            event_name: 'Training with breaks',
            period: [
                moment('2021-12-10T08:00:00.000Z'),
                moment('2021-12-10T08:00:00.000Z').clone().add(153, 'minutes'),
            ],
            period_formatted: '10.12(Fri) 12:00 - 10.12(Fri) 14:33',
        },
    ],
};
