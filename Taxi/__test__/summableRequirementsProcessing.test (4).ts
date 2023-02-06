import cloneDeep from 'lodash/cloneDeep';
import isNumber from 'lodash/isNumber';

import {toNumber} from '_utils/parser';

import summableRequirementsProcessing from '../summableRequirementsProcessing';
import {INTERVAL} from './const';

describe('summableRequirementsProcessing', () => {
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = summableRequirementsProcessing(INTERVAL);

    test('Проверяем преобразовались ли основные поля', () => {
        interval.summable_requirements.forEach(req => {
            expect(isNumber(req.max_price)).toBe(true);
            expect(req.included).toBeUndefined();
            expect(req.req_type).toBeUndefined();

            expect(isNumber(req.price.distance_multiplier)).toBe(true);
            expect(isNumber(req.price.included_distance)).toBe(true);
            expect(isNumber(req.price.included_time)).toBe(true);
            expect(isNumber(req.price.time_multiplier)).toBe(true);
        });
    });

    test('Проверяем требование на логику проставления типа', () => {
        expect(interval.summable_requirements[0].max_price).toBe(0);
        expect(interval.summable_requirements[0].multiplier)
            .toBe(toNumber(INTERVAL.summable_requirements[0].multiplier));

        expect(interval.summable_requirements[1].multiplier).toBeUndefined();
        expect(interval.summable_requirements[1].max_price)
            .toBe(toNumber(INTERVAL.summable_requirements[1].max_price));

        expect(interval.included_one_of).toEqual(['req1']);
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });
});
