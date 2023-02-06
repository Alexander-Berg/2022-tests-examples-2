import cloneDeep from 'lodash/cloneDeep';

import intervalsProcessing from '../intervalsProcessing';
import {INTERVAL} from './const';

describe('intervalsProcessing', () => {
    const INDEX = 3;
    const INITIAL_INTERVAL = cloneDeep(INTERVAL);
    const interval = intervalsProcessing(INTERVAL, INDEX);
    const interval2 = intervalsProcessing({...INTERVAL, waiting_price_type: undefined}, 0);

    test('Проверяем кастомные поля округения по времени/расстоянию', () => {
        const interval = intervalsProcessing(INTERVAL, 0);

        // проверяем кастомные поля округления по времени
        expect(interval).toHaveProperty('round_time_step', INTERVAL.zonal_prices[0].price.time_price_intervals[0].step);
        expect(interval).toHaveProperty('round_time_mode', INTERVAL.zonal_prices[0].price.time_price_intervals[0].mode);

        // проверяем кастомные поля округления по времени
        expect(interval).toHaveProperty(
            'round_distance_step',
            INTERVAL.special_taximeters[0].price.distance_price_intervals[0].step
        );
        expect(interval).toHaveProperty(
            'round_distance_mode',
            INTERVAL.special_taximeters[0].price.distance_price_intervals[0].mode
        );
    });

    test('Проверяем кастомное поле id, которое соответсвует его индексу в массиве', () => {
        expect(interval).toHaveProperty('interval_index', INDEX);
    });

    test('Проверяем поле waiting_price_type', () => {
        expect(interval).toHaveProperty('waiting_price_type', interval.waiting_price_type);
        // ессли в интервале нет поля waiting_price_type, должно быть проставлено дефолтное: per_minute
        expect(interval2).toHaveProperty('waiting_price_type', 'per_minute');
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(interval).not.toBe(INTERVAL);
        expect(INTERVAL).toEqual(INITIAL_INTERVAL);
    });
});
