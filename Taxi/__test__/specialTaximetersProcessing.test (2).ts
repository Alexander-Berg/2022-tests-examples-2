import cloneDeep from 'lodash/cloneDeep';

import specialTaximetersProcessing from '../specialTaximetersProcessing';
import {INTERVAL} from './const';
import {checkPriceItem} from './utils';

describe('specialTaximetersProcessing', () => {
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = specialTaximetersProcessing(INTERVAL);

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });

    test('Проверяем преобразовались ли основные поля', () => {
        expect(
            interval.special_taximeters[0].price.distance_price_intervals_meter_id
        ).toBe(INTERVAL.meters.length - 1);
        expect(
            interval.special_taximeters[0].price.time_price_intervals_meter_id
        ).toBe(INTERVAL.meters.length - 2);

        expect(
            interval.special_taximeters[1].price.distance_price_intervals_meter_id
        ).toBe(INTERVAL.meters.length + 1);
        expect(
            interval.special_taximeters[1].price.time_price_intervals_meter_id
        ).toBe(INTERVAL.meters.length * 1);
    });

    test('Проверяем что в поле price преобразовано', () => {
        interval.special_taximeters.forEach(transfer => {
            transfer.price.distance_price_intervals.forEach(checkPriceItem);
            transfer.price.distance_price_intervals.forEach(checkPriceItem);

            expect(transfer.distance_common_taximeter).toBe(undefined);
            expect(transfer.time_common_taximeter).toBe(undefined);
        });
    });
});
