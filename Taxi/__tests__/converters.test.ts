import {predictionConvertationConvertPayload, predictionSuggestsConvertPayload} from '../converters';

import {PREDICTION_CONVERTATION_MOCK, PREDICTION_SUGGESTS_MOCK} from './mocks';

test('predictionConvertationConvertPayload converts correctly', () => {
    const {payload: [tableItem], result} = PREDICTION_CONVERTATION_MOCK;

    expect(predictionConvertationConvertPayload(tableItem)).toStrictEqual(result);
});

test('predictionSuggestConvertPayload converts correctly', () => {
    const {payload: [period, skill], result} = PREDICTION_SUGGESTS_MOCK;

    expect(predictionSuggestsConvertPayload(period, skill)).toStrictEqual(result);
});
