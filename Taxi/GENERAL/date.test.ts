import MockDate from 'mockdate';
import moment from 'moment';

import {
    formatDate,
    formatTime,
    getCustomTime,
    getOffsetZoneTime,
    getZoneTime,
    roundOrderTime,
    roundTo5Minutes,
} from './date';

describe('utils/date', () => {
    describe('formatTime', () => {
        test('00:00', () => expect(formatTime(0, 0)).toBe('00:00'));
        test('12:00', () => expect(formatTime(12, 0)).toBe('12:00'));
    });
    describe('roundOrderTime', () => {
        test('сегодня 23:13 => сегодня 23:15', () =>
            expect(roundOrderTime(0, '23:13')).toEqual({
                day: 0,
                time: '23:15',
            }));
        test('сегодня 23:58 => завтра 00:00', () =>
            expect(roundOrderTime(0, '23:58')).toEqual({
                day: 1,
                time: '00:00',
            }));
    });
    describe('roundMinutes', () => {
        test('null => null', () => expect(roundTo5Minutes(null)).toEqual(null));
        test('25:00 => null', () => expect(roundTo5Minutes('25:00')).toEqual(null));
        test('00:00 => 00:00', () => expect(roundTo5Minutes('00:00')).toEqual('00:00'));
        test('00:02 => 00:00', () => expect(roundTo5Minutes('00:02')).toEqual('00:00'));
        test('00:03 => 00:05', () => expect(roundTo5Minutes('00:03')).toEqual('00:05'));
        test('00:58 => 01:00', () => expect(roundTo5Minutes('00:58')).toEqual('01:00'));
        test('23:58 => 24:00', () => expect(roundTo5Minutes('23:58')).toEqual('24:00'));
    });
    describe('getCustomTime', () => {
        afterAll(() => {
            MockDate.reset();
        });
        describe('getZoneTime', () => {
            it('Нормально показывает московское время', () => {
                MockDate.set('2019-03-15T03:56:43.000+0500');
                expect(getZoneTime('+0300').toISOString(true)).toBe(
                    '2019-03-15T01:56:43.000+03:00',
                );
                expect(getZoneTime('+1000').toISOString(true)).toBe(
                    '2019-03-15T08:56:43.000+10:00',
                );
                expect(getZoneTime('+0200').toISOString(true)).toBe(
                    '2019-03-15T00:56:43.000+02:00',
                );

                MockDate.set('2019-03-15T01:00:00.000+0500');
                expect(getZoneTime('+0200').toISOString(true)).toBe(
                    '2019-03-14T22:00:00.000+02:00',
                );
                expect(getZoneTime('+0500').toISOString(true)).toBe(
                    '2019-03-15T01:00:00.000+05:00',
                );
                expect(getZoneTime('+1000').toISOString(true)).toBe(
                    '2019-03-15T06:00:00.000+10:00',
                );

                MockDate.set('2019-03-14T22:00:00.000+0500');
                expect(getZoneTime('+0200').toISOString(true)).toBe(
                    '2019-03-14T19:00:00.000+02:00',
                );
                expect(getZoneTime('+1000').toISOString(true)).toBe(
                    '2019-03-15T03:00:00.000+10:00',
                );
            });
        });
        describe('offsetZoneTime', () => {
            it('Нормально добавляет дни к времени из временной зоны', () => {
                MockDate.set('2019-03-15T03:56:43.000+0500');
                expect(getOffsetZoneTime(0, '+0300').toISOString(true)).toBe(
                    '2019-03-15T01:56:43.000+03:00',
                );
                expect(getOffsetZoneTime(0, '+1000').toISOString(true)).toBe(
                    '2019-03-15T08:56:43.000+10:00',
                );
                expect(getOffsetZoneTime(0, '+0200').toISOString(true)).toBe(
                    '2019-03-15T00:56:43.000+02:00',
                );

                MockDate.set('2019-03-15T01:00:00.000+0500');
                expect(getOffsetZoneTime(0, '+0200').toISOString(true)).toBe(
                    '2019-03-14T22:00:00.000+02:00',
                );
                expect(getOffsetZoneTime(0, '+0500').toISOString(true)).toBe(
                    '2019-03-15T01:00:00.000+05:00',
                );
                expect(getOffsetZoneTime(0, '+1000').toISOString(true)).toBe(
                    '2019-03-15T06:00:00.000+10:00',
                );

                MockDate.set('2019-03-14T22:00:00.000+0500');
                expect(getOffsetZoneTime(0, '+0200').toISOString(true)).toBe(
                    '2019-03-14T19:00:00.000+02:00',
                );
                expect(getOffsetZoneTime(0, '+1000').toISOString(true)).toBe(
                    '2019-03-15T03:00:00.000+10:00',
                );
                expect(getOffsetZoneTime(0, '+1000').utcOffset()).toBe(600);
            });
        });
        describe('Заказ из временной зоны Екатеринбурга', () => {
            it('в Москву, где ещё предыдущие сутки', () => {
                MockDate.set('2019-03-15T03:56:43.000+0500');
                expect(getCustomTime(0, '02:15', '+0300').toISOString(true)).toBe(
                    '2019-03-15T02:15:00.000+03:00',
                );
            });
            it('во Владивосток, где уже день', () => {
                MockDate.set('2019-03-15T03:56:43.000+0500');
                expect(getCustomTime(0, '12:15', '+1000').toISOString(true)).toBe(
                    '2019-03-15T12:15:00.000+10:00',
                );
            });
            it('во Владивосток, с переходом через сутки', () => {
                MockDate.set('2019-03-15T21:00:00.000+0500');
                expect(
                    moment()
                        .utc()
                        .utcOffset('+1000')
                        .add(0, 'days')
                        .set('hour', 2)
                        .set('minutes', 15)
                        .set('seconds', 0)
                        .toISOString(true),
                ).toBe('2019-03-16T02:15:00.000+10:00');
                MockDate.set('2019-03-15T21:00:00.000+0500');
                expect(getCustomTime(0, '02:15', '+1000').toISOString(true)).toBe(
                    '2019-03-16T02:15:00.000+10:00',
                );
            });
        });
        it('правильно учитывает смещение для заказа, сделанного из Москвы для Калининграда', () => {
            MockDate.set('2019-03-15T00:30:00.000+0300');
            expect(moment().utc().utcOffset('+0200').startOf('day').toISOString(true)).toBe(
                '2019-03-14T00:00:00.000+02:00',
            );
            expect(getCustomTime(0, '23:55', '+0200').toISOString(true)).toBe(
                '2019-03-14T23:55:00.000+02:00',
            );
        });
    });
    describe('formatDate', () => {
        it('Форматирует далёкие даты без проблем', () => {
            MockDate.set('2019-03-15T00:30:00.000+0300');
            expect(formatDate('2019-06-01T00:00:00+0500')).toBe('2019.06.01, 00:00');
        });
        it('Если дата - сегодня, показывает только время', () => {
            MockDate.set('2019-03-15T18:00:00.000+0500');
            expect(formatDate('2019-03-15T19:00:00.000+0500')).toBe('19:00');

            MockDate.set('2019-03-15T23:00:00.000+0300');
            expect(formatDate('2019-03-16T00:30:00.000+0500')).toBe('00:30');
        });
    });
});
