import moment from 'moment';

import trimValues from '../trimValues';

describe('trimValues', () => {
    test('корректно тримит строку', () => {
        const str = ' hi ';
        const expected = 'hi';

        expect(trimValues(str)).toEqual(expected);
    });

    test('корректно тримит объект', () => {
        const obj = {
            a: ' asdf',
            v: ' sdf d '
        };

        const expected = {
            a: 'asdf',
            v: 'sdf d'
        };

        expect(trimValues(obj)).toEqual(expected);
    });

    test('корректно тримит массив', () => {
        const obj = [' hello', ' world ', 'good', undefined, null, [], {}];
        const expected = ['hello', 'world', 'good', undefined, null, [], {}];

        expect(trimValues(obj)).toEqual(expected);
    });

    test('корректно тримит массив в объекте', () => {
        const obj = {
            array: [' hello', 'hi ', ' ho ', 'hihih']
        };

        const expected = {
            array: ['hello', 'hi', 'ho', 'hihih']
        };

        expect(trimValues(obj)).toEqual(expected);
    });

    test('корректно тримит массив объектов', () => {
        const obj = [{hello: 'hello  '}, 'world', {good: '  good'}];
        const expected = [{hello: 'hello'}, 'world', {good: 'good'}];

        expect(trimValues(obj)).toEqual(expected);
    });

    test('корректно тримит объект любой вложенности', () => {
        const obj = {
            a: ' asdf',
            v: ' sdf d ',
            object: {
                noNew: '  ывап  ',
                obj: {
                    smile: ' :) '
                }
            }
        };

        const expected = {
            a: 'asdf',
            v: 'sdf d',
            object: {
                noNew: 'ывап',
                obj: {
                    smile: ':)'
                }
            }
        };

        expect(trimValues(obj)).toEqual(expected);
    });

    test('корректно тримит объект с полями не типа string', () => {
        const obj: Indexed = {
            a: ' asdf',
            v: ' sdf d ',
            dfg: 1234,
            predivate: undefined,
            object: {
                new: true,
                noNew: '  ывап  '
            },
            array: [' hello', 'hi ', ' ho ', 'hihih'],
            some: null
        };

        const expected: Indexed = {
            a: 'asdf',
            v: 'sdf d',
            dfg: 1234,
            predivate: undefined,
            object: {
                new: true,
                noNew: 'ывап'
            },
            array: ['hello', 'hi', 'ho', 'hihih'],
            some: null
        };

        expect(trimValues(obj)).toEqual(expected);
    });

    test('корректно обрабатывает пустой объект', () => {
        expect(trimValues({})).toEqual({});
        expect(trimValues([])).toEqual([]);
    });

    test('корректно обрабатывает null и undefined', () => {
        expect(trimValues(null)).toEqual(null);
        expect(trimValues(undefined)).toEqual(undefined);
    });

    test('корректно обрабатывает moment', () => {
        const date = moment();

        expect(trimValues(date)).toStrictEqual(date);
    });
});
