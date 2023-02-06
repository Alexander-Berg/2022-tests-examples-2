/* eslint-disable max-len */
import MockDate from 'mockdate';
import moment from 'moment';

import {mapClientDueToServer} from './order';

describe('moment', () => {
    beforeEach(() => MockDate.reset());
    afterAll(() => MockDate.reset());
    test('он должен работать с временной зоной', () => {
        expect(moment('2019-01-01 12:00+00:00').utcOffset('+0500').format()).toBe(
            '2019-01-01T17:00:00+05:00',
        );
    });
    test('SOD', () => {
        MockDate.set('2019-03-14T12:00:00', '0500');
        expect(
            moment().utcOffset('+0300', true).startOf('day').set('hour', 2).toISOString(true),
        ).toBe('2019-03-14T02:00:00.000+03:00');
    });
});

describe('OrderSelector', () => {
    describe('mapClientDueToServer', () => {
        beforeEach(() => MockDate.reset());
        afterAll(() => MockDate.reset());
        test('Когда выбрано - "прямо сейчас" - возвращается undefined', () => {
            MockDate.reset();
            expect(mapClientDueToServer('+0000', {day: 0, time: '07:25', due: 0})).toBe(undefined);
        });
        test.skip('Когда выбрано "через десять минут" - должно возвращаться текущее время +10 мин в указанной временной зоне', () => {
            MockDate.set('2019-02-27T16:00:00.000', -300);
            expect(moment().format()).toBe('2019-02-27T16:00:00+05:00');
            expect(new Date().getTimezoneOffset()).toBe(-300);
            expect(mapClientDueToServer('+0300', {due: 10})).toBe('2019-02-27T14:10:00.000+03:00');
        });
        test('Когда выбрано конкретное время сегодня - оно должно возвращаться с временной зоной', () => {
            MockDate.set('2019-02-27T03:45:00.000Z', '00:00');
            expect(
                mapClientDueToServer('+0500', {
                    day: 0,
                    time: '18:45',
                    due: 'custom',
                }),
            ).toBe('2019-02-27T18:45:00.000+05:00');
            MockDate.set('2019-02-24T23:45:00', '+0500');
            expect(
                mapClientDueToServer('+0300', {
                    day: 0,
                    time: '18:45',
                    due: 'custom',
                }),
            ).toBe('2019-02-24T18:45:00.000+03:00');
        });
    });
});
