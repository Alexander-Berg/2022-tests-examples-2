import {RestrictionTypes} from '@yandex-taxi/corp-staff';
import {isCorrectHour, isCorrectMinute} from '@yandex-taxi/corp-utils/date';

import {identity} from 'lodash';
import {validate} from 'perfecto';

import {restrictionValidator} from './validation';

describe('restrictionValidator', () => {
    const v = object => validate(restrictionValidator({t: identity}))({object});

    describe('start_time, end_time', () => {
        test('Оба поля - обязательные', async () => {
            const errors = await v({days: {mo: true}, type: RestrictionTypes.WeeklyDate});
            expect(errors).toEqual([
                {path: [], message: 'validation.restrictions.time.required'},
                {path: ['start_time'], message: 'validation.required'},
                {path: ['end_time'], message: 'validation.required'},
            ]);
        });
        test('Проверяется формат', async () => {
            expect(
                await v({
                    days: {mo: true},
                    start_time: '2',
                    end_time: '12:00',
                    type: RestrictionTypes.WeeklyDate,
                }),
            ).toEqual([
                {
                    path: ['start_time'],
                    message: 'validation.restrictions.time.format',
                },
            ]);
            expect(
                await v({
                    days: {mo: true},
                    start_time: '02:00',
                    end_time: '22',
                    type: RestrictionTypes.WeeklyDate,
                }),
            ).toEqual([
                {
                    path: ['end_time'],
                    message: 'validation.restrictions.time.format',
                },
            ]);
        });
        test('Часы и минуты попадают в рамки', () => undefined);
    });

    describe('days', () => {
        test('Хотя бы один день должен быть выбран', async () => {
            const errors = await v({
                days: [],
                start_time: '12:00',
                end_time: '13:00',
                type: RestrictionTypes.WeeklyDate,
            });
            expect(errors).toEqual([
                {
                    path: ['days'],
                    message: 'validation.restrictions.days.required',
                },
            ]);
        });
    });

    describe('isCorrectHour', () => {
        test('Возвращает true для корректных или пустых значений', () => {
            expect(isCorrectHour('12:00')).toBeTruthy();
            expect(isCorrectHour('1:00')).toBeTruthy();
            expect(isCorrectHour('0:00')).toBeTruthy();
            expect(isCorrectHour('24:00')).toBeTruthy();
        });
        test('Возвращает false для некорректных значений', () => {
            expect(isCorrectHour(':00')).toBeFalsy();
            expect(isCorrectHour('25:00')).toBeFalsy();
        });
    });

    describe('isCorrectMinute', () => {
        test('Возвращает true для корректных или пустых значений', () => {
            expect(isCorrectMinute('00:00')).toBeTruthy();
            expect(isCorrectMinute('0:01')).toBeTruthy();
            expect(isCorrectMinute('02:1')).toBeTruthy();
            expect(isCorrectMinute('0:59')).toBeTruthy();
        });
        test('Возвращает false для некорректных значений', () => {
            expect(isCorrectMinute('12:')).toBeFalsy();
            expect(isCorrectMinute('12:60')).toBeFalsy();
        });
    });
});
