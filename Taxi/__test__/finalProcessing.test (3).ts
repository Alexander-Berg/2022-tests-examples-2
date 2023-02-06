import cloneDeep from 'lodash/cloneDeep';

import {CategoryTypes} from '../../../../../types';
import finalProcessing from '../finalProcessing';
import {INTERVAL} from './const';

describe('finalProcessing', () => {
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = finalProcessing(INTERVAL);
    const interval2 = finalProcessing({...INTERVAL, category_type: null});

    test('Проверем финальный процессинг', () => {
        expect(interval.included_one_of).toBe(undefined);
        expect(interval.category_type).toBe(CategoryTypes.CallCenter);

        expect(interval2.category_type).toBe(CategoryTypes.Aplication);
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });
});
