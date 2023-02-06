import {urlWithLang, formatCurrency, carNumber} from '../formatter';

describe('utils:formatter', () => {
    describe('urlWithLang', () => {
        it('К относительноый ссылки добавляется язык', () => {
            expect(urlWithLang('/', 'ru')).toBe('/?lang=ru');
        });

        it('К абсолютной ссылке добавляется язык', () => {
            expect(urlWithLang('http://ya.ru', 'ru')).toBe('http://ya.ru?lang=ru');
        });

        it('К ссылке с гет параметрами добавляется язык', () => {
            expect(urlWithLang('/blog?page=1', 'en')).toBe('/blog?lang=en&page=1');
        });

        it('К ссылке с хешом добавляется язык', () => {
            expect(urlWithLang('/path#hash', 'en')).toBe('/path?lang=en#hash');
        });

        it('К ссылке с хешом и гет параметрами добавляется язык', () => {
            expect(urlWithLang('/path?foo=baz#hash', 'en')).toBe('/path?foo=baz&lang=en#hash');
        });
    });

    describe('formatCurrency', () => {
        it('Цена верно форматируется', () => {
            expect(formatCurrency('100 $SIGN$$CURRENCY$', 'RUB')).toBe('100 ₽');
            expect(formatCurrency('100 $SIGN$$CURRENCY$', 'ПОПУГАЕВ')).toBe('100 ПОПУГАЕВ');
        });

        it('Если price нет - возвращает пустую строку', () => {
            expect(formatCurrency(undefined, 'RUB')).toBe('');
        });
    });

    describe('carNumber', () => {
        it('Обычный номер машины форматируется верно', () => {
            expect(carNumber('c302ab199')).toEqual({
                raw: 'c302ab199',
                region: '199',
                number: ['c', '302', 'ab'],
                type: 'rus'
            });
        });

        it('Жёлтый номер машины форматируется верно', () => {
            expect(carNumber('md30299')).toEqual({
                raw: 'md30299',
                region: '99',
                number: ['md', '302'],
                type: 'rus-yellow'
            });
        });

        it('Пробелы игнорируются', () => {
            expect(carNumber(' md 30 2 9 9 ')).toEqual({
                raw: 'md30299',
                region: '99',
                number: ['md', '302'],
                type: 'rus-yellow'
            });
        });

        it('Неизвестный номер машины не форматируется', () => {
            expect(carNumber('ABCD111')).toEqual({raw: 'ABCD111', type: 'unknown'});
        });

        it('Пустой номер возвращает undefined', () => {
            expect(carNumber()).toBe(undefined);
        });
    });
});
