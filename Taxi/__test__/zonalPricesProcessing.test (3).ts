import cloneDeep from 'lodash/cloneDeep';
import {MULTIZONE} from '../../../../../consts';
import zonalPricesProcessing from '../zonalPricesProcessing';
import {INTERVAL} from './const';

describe('zonalPricesProcessing', () => {
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = zonalPricesProcessing(INTERVAL);

    test('Проверяем корректность замены destination & source', () => {
        expect(interval.zonal_prices[0].destination).toBe(INTERVAL.zonal_prices[0].destination);
        expect(interval.zonal_prices[0].source).toBe(INTERVAL.zonal_prices[0].source);

        expect(interval.zonal_prices[1].destination).toBe(MULTIZONE);
        expect(interval.zonal_prices[1].source).toBe(MULTIZONE);
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });
});
