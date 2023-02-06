import cloneDeep from 'lodash/cloneDeep';

import {REQ_TYPES} from '../../../../consts';
import summableRequirementsProcessing from '../summableRequirementsProcessing';
import {INTERVAL} from './const';

describe('summableRequirementsProcessing', () => {
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = summableRequirementsProcessing(INTERVAL);

    test('Проверяем кастомные поля req_type & included', () => {
        expect(interval.summable_requirements?.[0].req_type).toBe(REQ_TYPES.multiplier);
        expect(interval.summable_requirements?.[0].multiplier).toBe(INTERVAL.summable_requirements?.[0].multiplier);
        expect(interval.summable_requirements?.[0].included).toBe(true);

        expect(interval.summable_requirements?.[1].req_type).toBe(REQ_TYPES.fixed);
        expect(interval.summable_requirements?.[1].included).toBeFalsy();
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });
});
