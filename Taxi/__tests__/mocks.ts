import moment from 'moment-timezone';

import {ConvertersTestDataType} from 'types/tests';

import {predictionConvertationConvertPayload, predictionSuggestsConvertPayload} from '../converters';

export const PREDICTION_CONVERTATION_MOCK: ConvertersTestDataType<typeof predictionConvertationConvertPayload> = {
    payload: [[{
        average_handle_time: 54,
        break_percentage: undefined,
        from: moment('2021-08-25T00:00:00+03:00'),
        id: 246,
        key: '0',
        service_time: 4,
        sla: 95,
        to: moment('2021-08-28T23:59:00+03:00'),
        average_sessions_count: 2,
    }]],
    result: [{
        record_target_from: '2021-08-25T00:00:00+03:00',
        record_target_to: '2021-08-28T23:59:00+03:00',
        settings: {
            service_time: 4,
            average_handle_time: 54,
            sla: 0.95,
            break_percentage: undefined,
            absence_periods_percentage: undefined,
            average_sessions_count: 2,
        },
        calculation_id: 246,
    }],
};

export const PREDICTION_SUGGESTS_MOCK: ConvertersTestDataType<typeof predictionSuggestsConvertPayload> = {
    payload: [
        [moment('2021-08-01T00:00:00+03:00'), moment('2021-08-08T23:59:00+03:00')],
        'lavka',
    ],
    result: {
        entity_target_from: '2021-08-01T00:00:00+03:00',
        entity_target_to: '2021-08-08T23:59:59+03:00',
        skill: 'lavka',
        source: 'custom',
    },
};
