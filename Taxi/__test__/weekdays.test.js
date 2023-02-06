import {dayOfWeekToRange} from '../weekdays';

describe('dayOfWeekToRange', function () {
    test('dayOfWeekToRange, пустая строка', () => {
        expect(dayOfWeekToRange('')).toEqual([]);
    });
    test('dayOfWeekToRange, дни через запятую', () => {
        expect(dayOfWeekToRange('1,3,5')).toEqual([1, 3, 5]);
    });
    test('dayOfWeekToRange, дни через дефис', () => {
        expect(dayOfWeekToRange('1-3, 5-7')).toEqual([1, 2, 3, 5, 6, 7]);
    });
    test('dayOfWeekToRange, дни через запятую и через дефис', () => {
        expect(dayOfWeekToRange('1-2,4,6-7')).toEqual([1, 2, 4, 6, 7]);
    });
});
