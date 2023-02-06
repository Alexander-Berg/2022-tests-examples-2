import cloneDeep from 'lodash/cloneDeep';

import {SpecialTaximeter} from '../../../../types';
import specialTaximetersProcessing from '../specialTaximetersProcessing';
import {INTERVAL} from './const';

describe('specialTaximetersProcessing', () => {
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = specialTaximetersProcessing(INTERVAL);

    test('Проверяем кастомные счетчики по дистанции/времени', () => {
        interval.special_taximeters.forEach((transfer: SpecialTaximeter) => {
            expect(transfer.time_common_taximeter).toBe(true);
            expect(transfer.distance_common_taximeter).toBe(false);
        });
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });
});
