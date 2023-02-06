import cloneDeep from 'lodash/cloneDeep';
import isBoolean from 'lodash/isBoolean';
import isNumber from 'lodash/isNumber';

import zonalPricesProcessing from '../zonalPricesProcessing';
import {INTERVAL} from './const';
import {checkPriceItem} from './utils';

describe('zonalPricesProcessing', () => {
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = zonalPricesProcessing(INTERVAL);

    test('Проверяем преобразовались ли основные поля', () => {
        interval.zonal_prices.forEach(item => {
            expect(item).toHaveProperty('route_without_jams');
            expect(isBoolean(item.route_without_jams)).toBe(true);

            expect(interval.zonal_prices[0].destination).toBe(INTERVAL.zonal_prices[0].destination);
            expect(interval.zonal_prices[0].source).toBe(INTERVAL.zonal_prices[0].source);

            expect(interval.zonal_prices[1].destination).toBeNull();
            expect(interval.zonal_prices[1].source).toBeNull();

            expect(isNumber(item.price.once)).toBe(true);
            expect(isNumber(item.price.minimal)).toBe(true);

            item.price.distance_price_intervals.forEach(checkPriceItem);
            item.price.distance_price_intervals.forEach(checkPriceItem);
        });
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });
});
