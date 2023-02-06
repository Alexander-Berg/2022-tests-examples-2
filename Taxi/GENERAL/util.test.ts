import {AnalystEntity, AnalystOrderSource} from 'types/analyst';

import {aggregateHexesOrdersValuesByMonth, analyticIntervalsWithOpacity, calculateOpacity, MAX_OPACITY} from './util';
import {monthOrdersOfSourceMock} from './util.mock';

describe('calculateOpacity()', () => {
    it('should return 0 if value is less or equal than minimal threshold #1', () => {
        const intervals = [1, 2, 3];

        expect(serializeFloat(calculateOpacity(1, intervals))).toBe('0.40');
        expect(calculateOpacity(0, intervals)).toBe(0);
    });

    it('should return 0 if value is less or equal than minimal threshold #2', () => {
        const intervals = [0, 2, 3];

        expect(calculateOpacity(0, intervals)).toBe(0);
    });

    it('should return opacity between min and max if medium value', () => {
        const intervals = [1, 3, 5];

        expect(calculateOpacity(2, intervals)).toBeLessThan(MAX_OPACITY);
        expect(calculateOpacity(2, intervals)).toBeGreaterThan(0);
    });

    it('should return MAX_OPACITY if the value is in the top segment', () => {
        const intervals = [1, 3, 5, 7];

        const opacity6 = calculateOpacity(6, intervals);
        const opacity7 = calculateOpacity(7, intervals);

        expect(serializeFloat(opacity6)).toBe(serializeFloat(MAX_OPACITY));
        expect(serializeFloat(opacity7)).toBe(serializeFloat(MAX_OPACITY));
    });

    it('should return MAX_OPACITY if the value is greater than top segment', () => {
        const intervals = [1, 3, 5, 7];

        const opacity8 = calculateOpacity(8, intervals);

        expect(serializeFloat(opacity8)).toBe(serializeFloat(MAX_OPACITY));
    });
});

describe('aggregateOrdersValues()', () => {
    it('should return average price and count orders for food orders', async () => {
        const {avgPrice, ordersCountPerDay} = aggregateHexesOrdersValuesByMonth(
            monthOrdersOfSourceMock,
            AnalystOrderSource.EDA
        );

        expect({avgPrice: serializeFloat(avgPrice), ordersCountPerDay}).toStrictEqual({
            avgPrice: '1699.77',
            ordersCountPerDay: 46
        });
    });

    it('should return average price and count orders for lavka orders', async () => {
        const {avgPrice, ordersCountPerDay} = aggregateHexesOrdersValuesByMonth(
            monthOrdersOfSourceMock,
            AnalystOrderSource.LAVKA
        );

        expect({avgPrice: serializeFloat(avgPrice), ordersCountPerDay}).toStrictEqual({
            avgPrice: '930.16',
            ordersCountPerDay: 14
        });
    });

    it('should return average price and count orders for taxi orders', async () => {
        const {avgPrice, ordersCountPerDay} = aggregateHexesOrdersValuesByMonth(
            monthOrdersOfSourceMock,
            AnalystOrderSource.TAXI
        );

        expect({avgPrice: serializeFloat(avgPrice), ordersCountPerDay}).toStrictEqual({
            avgPrice: '646.18',
            ordersCountPerDay: 395
        });
    });
});

describe('analyticIntervalsWithOpacity()', () => {
    it('should return analyticIntervalsWithOpacity', async () => {
        const {intervals, opacity} = analyticIntervalsWithOpacity(
            {
                entity: AnalystEntity.SOCDEM_C1C2RES,
                intervals: [1, 137, 410, 796, 4032, 13626],
                cityGeoId: 213
            },
            AnalystEntity.SOCDEM_C1C2RES
        );

        expect({intervals, opacity: opacity?.map((item) => serializeFloat(item))}).toStrictEqual({
            intervals: [1, 137, 410, 796, 4032, 13626],
            opacity: ['0.16', '0.32', '0.48', '0.64', '0.80']
        });
    });
});

function serializeFloat(float: number): string {
    return float.toFixed(2);
}
