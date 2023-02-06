import {hasValue} from '../hasValue';

describe('hasValue', () => {
    test('Корректно работает если нет пустых полей', () => {
        const obj = {
            foo: true,
            bar: 'baz'
        };

        expect(hasValue(obj)).toBe(true);
    });
    test('Корректно работает если не все поля пустые', () => {
        const obj = {
            foo: 'baz',
            bar: null
        };

        expect(hasValue(obj)).toBe(true);
    });
    test('Корректно работает если все поля пустые', () => {
        const obj = {
            foo: undefined,
            bar: null
        };

        expect(hasValue(obj)).toBe(false);
    });

    test('Корректно работает если в поле пустая строка', () => {
        const obj = {
            foo: '',
            bar: null
        };

        expect(hasValue(obj)).toBe(false);
    });

    test('Корректно работает объект пустой', () => {
        const obj1 = null;
        const obj2 = undefined;
        const obj3 = {};

        expect(hasValue(obj1)).toBe(false);
        expect(hasValue(obj2)).toBe(false);
        expect(hasValue(obj3)).toBe(false);
    });

    test('Корректно работает если объект вложенный, но пустыми полями', () => {
        const obj = {
            a: {
                b: {
                    c: '',
                    d: {
                        f: null,
                        g: undefined,
                    },
                    h: []
                },
                e: false
            }
        };

        expect(hasValue(obj)).toBe(false);
    });
});
