/* global i18n */
import moment from 'moment';
import _ from 'lodash';
import {formatDate, humanizeTime} from '../dateFormatter';

describe('utils:dateFormatter', () => {
    describe('formatDate', () => {
        const now = new Date();
        const oldYear = new Date(2000, 10, 10);

        test('Текущая дата должна возвращать краткую форму', () => {
            expect(formatDate(moment(now))).toBe(moment(now).format('DD.MM, HH:mm'));
        });

        test('Прошлогодняя дата должна возвращать полную форму', () => {
            expect(formatDate(moment(oldYear))).toBe(moment(oldYear).format('DD.MM.YYYY, HH:mm'));
        });
    });

    describe('humanizeTime', () => {
        const futureTime = moment();
        let oldTime = moment();

        beforeEach(() => {
            oldTime = moment();
        });

        futureTime.add(1, 'h');

        test('Дата в будущем возвращает фразу вида "Сегодня, в 10:00"', () => {
            expect(humanizeTime(futureTime.toISOString(), i18n)).toBe(`Сегодня, в ${futureTime.format('HH:mm')}`);
        });

        test('Сегодняшняя дата возвращает фразу вида "Сегодня, в 10:00" ', () => {
            oldTime.subtract(1, 'm');

            expect(humanizeTime(oldTime.toISOString(), i18n)).toBe(`Сегодня, в ${oldTime.format('HH:mm')}`);
        });

        test('Вчерашняя дата возвращает фразу вида "Вчера, в 10:00"', () => {
            oldTime.subtract(1, 'd');

            expect(humanizeTime(oldTime.toISOString(), i18n)).toBe(`Вчера, в ${oldTime.format('HH:mm')}`);
        });

        test('Дата на этой недели возвращает фразу вида "Вторник, в 10:00"', () => {
            oldTime.subtract(3, 'd');

            expect(humanizeTime(oldTime.toISOString(), i18n)).toBe(
                `${_.capitalize(oldTime.format('dddd'))}, в ${oldTime.format('HH:mm')}`
            );
        });

        test('Дата прошлого месяца возвращает фразу вида "1 февраля, в 10:00', () => {
            oldTime.subtract(1, 'M');

            if (oldTime.year() !== new Date().getFullYear()) {
                expect(humanizeTime(oldTime.toISOString(), i18n)).toBe(
                    `${oldTime.format('DD MMMM YYYY')}, в ${oldTime.format('HH:mm')}`
                );
            } else {
                expect(humanizeTime(oldTime.toISOString(), i18n)).toBe(
                    `${oldTime.format('DD MMMM')}, в ${oldTime.format('HH:mm')}`
                );
            }
        });

        test('Прошлогодняя дата возвращает фразу вида "1 февраля 2000, в 10:00', () => {
            oldTime.subtract(1, 'y');

            expect(humanizeTime(oldTime.toISOString(), i18n)).toBe(
                `${oldTime.format('DD MMMM YYYY')}, в ${oldTime.format('HH:mm')}`
            );
        });
    });
});
