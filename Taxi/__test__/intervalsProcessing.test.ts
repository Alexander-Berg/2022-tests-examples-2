import cloneDeep from 'lodash/cloneDeep';

import intervalsProcessing from '../intervalsProcessing';
import {INTERVAL} from './const';

describe('intervalsProcessing', () => {
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = intervalsProcessing(INTERVAL);

    test('Проверяем преобразовались ли основные поля', () => {
        expect(interval.minimal).toBe(1);
        expect(interval.waiting_price).toBe(1);
        expect(interval.waiting_included).toBe(1);
        expect(interval.round_distance_step).toBe(1);
        expect(interval.round_time_step).toBe(1);
        expect(interval.paid_cancel_fix).toBe(1);
        expect(interval.waiting_taximeter).toBe(undefined);
    });

    test('Проверяем что лишние поля были удалены', () => {
        expect(interval).not.toHaveProperty('interval_index');
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });
});
