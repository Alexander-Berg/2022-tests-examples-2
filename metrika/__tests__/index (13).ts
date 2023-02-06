import i18n, { i18nRaw } from '../index';
import * as keyset from '../__tests__.i18n';

describe('i18n', () => {
    const lang = 'ru';
    const i18nFactory = i18n(lang, keyset);

    it('returns function', () => {
        expect(typeof i18nFactory === 'function').toBe(true);
    });

    describe('i18nFactory', () => {
        it('returns string', () => {
            expect(typeof i18nFactory('fake-key') === 'string').toBe(true);
        });

        it('returns empty string if invalid key provided', () => {
            expect(i18nFactory('fake-key')).toBe('');
        });

        it('returns string with params expanded', () => {
            expect(i18nFactory('test-params', { param: 'сюрпризом' })).toBe(
                'тестовые параметры с сюрпризом',
            );
        });

        it('returns string with params expanded into empty string if no value provided', () => {
            expect(i18nFactory('test-params')).toBe('тестовые параметры с ');
        });

        it('handles {count: 1} option for pluralization', () => {
            expect(i18nFactory('test-plural', { count: 1 })).toBe('1 штука');
        });

        it('handles {count: 2} option for pluralization', () => {
            expect(i18nFactory('test-plural', { count: 2 })).toBe('2 штуки');
        });

        it('handles {count: 5} option for pluralization', () => {
            expect(i18nFactory('test-plural', { count: 5 })).toBe('5 штук');
        });

        it('handles {count: 0} option for pluralization', () => {
            expect(i18nFactory('test-plural', { count: 0 })).toBe('Пустота');
        });
    });
});

describe('i18nRaw', () => {
    const lang = 'ru';
    const i18nRawFactory = i18nRaw(lang, keyset);

    it('returns function', () => {
        expect(typeof i18nRawFactory === 'function').toBe(true);
    });

    describe('i18nRawFactory', () => {
        it('returns array', () => {
            expect(Array.isArray(i18nRawFactory('fake-key'))).toBe(true);
        });
    });

    it('returns array with params expanded', () => {
        expect(i18nRawFactory('test-params', { param: 'сюрпризом' })).toEqual([
            'тестовые параметры с ',
            'сюрпризом',
        ]);
    });

    it('handles {count: 1} option for pluralization', () => {
        expect(i18nRawFactory('test-plural', { count: 1 })).toEqual([
            '',
            1,
            ' штука',
        ]);
    });

    it('handles {count: 2} option for pluralization', () => {
        expect(i18nRawFactory('test-plural', { count: 2 })).toEqual([
            '',
            2,
            ' штуки',
        ]);
    });

    it('handles {count: 5} option for pluralization', () => {
        expect(i18nRawFactory('test-plural', { count: 5 })).toEqual([
            '',
            5,
            ' штук',
        ]);
    });

    it('handles {count: 0} option for pluralization', () => {
        expect(i18nRawFactory('test-plural', { count: 0 })).toEqual([
            'Пустота',
        ]);
    });
});
