import cloneDeep from 'lodash/cloneDeep';

import finalProcessing from '../finalProcessing';
import {INTERVAL} from './const';

describe('finalProcessing', () => {
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = finalProcessing(INTERVAL);

    test('Проверяем преобразовались ли основные поля', () => {
        expect(interval.round_distance_step).toBeUndefined();
        expect(interval.round_distance_mode).toBeUndefined();
        expect(interval.round_time_step).toBeUndefined();
        expect(interval.round_time_mode).toBeUndefined();
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });
});
