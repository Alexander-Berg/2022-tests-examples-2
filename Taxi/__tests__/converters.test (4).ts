import {convertLoadParamsForRequest} from '../converters';

import {
    ANOTHER_PERFECT_MOCK_FOR_LOAD,
    PERFECT_MOCK_FOR_LOAD,
    MOCK_WITHOUT_STEP_MINUTES_FOR_LOAD,
    MOCK_WITHOUT_SECOND_PERIOD_FOR_LOAD,
    MOCK_WITHOUT_PERIODS_FOR_LOAD,
    MOCK_WITHOUT_PERIOD_FOR_LOAD,
} from './mocks';

test('convertLoadParamsForRequest do with perfect params', () => {
    const [params] = PERFECT_MOCK_FOR_LOAD.payload;

    expect(convertLoadParamsForRequest(params))
        .toStrictEqual(PERFECT_MOCK_FOR_LOAD.result);
});

test('convertLoadParamsForRequest do with another perfect params', () => {
    const [params] = ANOTHER_PERFECT_MOCK_FOR_LOAD.payload;

    expect(convertLoadParamsForRequest(params))
        .toStrictEqual(ANOTHER_PERFECT_MOCK_FOR_LOAD.result);
});

test('convertLoadParamsForRequest do without "step_minutes"', () => {
    const [params] = MOCK_WITHOUT_STEP_MINUTES_FOR_LOAD.payload;

    expect(convertLoadParamsForRequest(params))
        .toStrictEqual(MOCK_WITHOUT_STEP_MINUTES_FOR_LOAD.result);
});

test('convertLoadParamsForRequest do with normal period[0] and empty period[1]', () => {
    try {
        const [params] = MOCK_WITHOUT_SECOND_PERIOD_FOR_LOAD.payload;

        convertLoadParamsForRequest(params);
    } catch (e) {
        expect(e.message).toBe(MOCK_WITHOUT_SECOND_PERIOD_FOR_LOAD.error);
    }
});

test('convertLoadParamsForRequest do with empty period[0] and empty period[1]', () => {
    try {
        const [params] = MOCK_WITHOUT_PERIODS_FOR_LOAD.payload;

        convertLoadParamsForRequest(params);
    } catch (e) {
        expect(e.message).toBe(MOCK_WITHOUT_PERIODS_FOR_LOAD.error);
    }
});

test('convertLoadParamsForRequest do with empty period', () => {
    try {
        const [params] = MOCK_WITHOUT_PERIOD_FOR_LOAD.payload;

        convertLoadParamsForRequest(params);
    } catch (e) {
        expect(e.message).toBe(MOCK_WITHOUT_PERIOD_FOR_LOAD.error);
    }
});
