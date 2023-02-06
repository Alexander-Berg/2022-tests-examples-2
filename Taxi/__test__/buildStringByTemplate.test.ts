import {buildStringByTemplate} from '../buildStringByTemplate';

describe('buildStringByTemplate', () => {
    test('корректно подставляет один параметр', () => {
        const string = 'Hello, {name}!';
        const params = {
            name: 'world'
        };

        const expected = 'Hello, world!';
        expect(buildStringByTemplate(string, params)).toEqual(expected);
    });

    test('корректно подставляет несколько параметров', () => {
        const string = 'Hello, {name}! How are you, {some}?';
        const params = {
            name: 'world',
            some: 'man'
        };

        const expected = 'Hello, world! How are you, man?';
        expect(buildStringByTemplate(string, params)).toEqual(expected);
    });

    test('корректно подставляет повторяющиеся параметры', () => {
        const string = 'Hello, {name}! How are you, {some}? I know that {name} is hungry.';
        const params = {
            name: 'world',
            some: 'man'
        };

        const expected = 'Hello, world! How are you, man? I know that world is hungry.';
        expect(buildStringByTemplate(string, params)).toEqual(expected);
    });

    test('корректно обрабатывает несуществующий в мапе параметр', () => {
        const string = 'Hello, {name}!';
        const params = {
            hello: 'world'
        };

        expect(buildStringByTemplate(string, params)).toEqual(string);
    });

    test('возвращает исходную строку, если нет параметров', () => {
        const string1 = 'It is beautiful!';
        const params = {};

        expect(buildStringByTemplate(string1, params)).toEqual(string1);

        const string2 = 'Hello, {name}!';

        expect(buildStringByTemplate(string2, params)).toEqual(string2);
    });

    test('корректно обрабатывает пустую строку', () => {
        expect(buildStringByTemplate('', {})).toEqual('');
    });

    test('корректно обрабатывает null и undefined', () => {
        expect(buildStringByTemplate(null, null)).toEqual(null);
        expect(buildStringByTemplate(undefined, undefined)).toEqual(undefined);
    });

    test('корректно подставляет один параметр c опцией запрета пропуска', () => {
        const string = 'Hello, {name}!';
        const params = {
            name: 'world'
        };

        const expected = 'Hello, world!';
        expect(buildStringByTemplate(string, params, false)).toEqual(expected);
    });

    test('корректно подставляет несколько параметров c опцией запрета пропуска', () => {
        const string = 'Hello, {name}! How are you, {some}?';
        const params = {
            name: 'world',
            some: 'man'
        };

        const expected = 'Hello, world! How are you, man?';
        expect(buildStringByTemplate(string, params, false)).toEqual(expected);
    });

    test('корректно подставляет повторяющиеся параметры c опцией запрета пропуска', () => {
        const string = 'Hello, {name}! How are you, {some}? I know that {name} is hungry.';
        const params = {
            name: 'world',
            some: 'man'
        };

        const expected = 'Hello, world! How are you, man? I know that world is hungry.';
        expect(buildStringByTemplate(string, params, false)).toEqual(expected);
    });

    test('корректно обрабатывает несуществующий в мапе параметр c опцией запрета пропуска', () => {
        const string = 'Hello, {name}!';
        const params = {
            hello: 'world'
        };

        expect(buildStringByTemplate(string, params, false)).toEqual(undefined);
    });

    test('возвращает исходную строку, если нет параметров c опцией запрета пропуска', () => {
        const string1 = 'It is beautiful!';
        const params = {};

        expect(buildStringByTemplate(string1, params, false)).toEqual(string1);
    });

    test('возвращает undefined если не хватает параметров для строки c опцией запрета пропуска', () => {
        const string = 'Hello, {name}! How are you, {some}?';
        const params = {
            name: 'world',
        };
        expect(buildStringByTemplate(string, params, false)).toEqual(undefined);
    });

    test('возвращает строку если параметров больше чем надо c опцией запрета пропуска', () => {
        const string = 'Hello, {name}! How are you, {some}?';
        const params = {
            name: 'world',
            some: 'man',
            other: 'other'
        };

        const expected = 'Hello, world! How are you, man?';
        expect(buildStringByTemplate(string, params, false)).toEqual(expected);
    });

    test('корректно обрабатывает пустую строку c опцией запрета пропуска', () => {
        expect(buildStringByTemplate('', {}, false)).toEqual('');
    });

    test('корректно обрабатывает null и undefined c опцией запрета пропуска', () => {
        expect(buildStringByTemplate(null, null, false)).toEqual(null);
        expect(buildStringByTemplate(undefined, undefined, false)).toEqual(undefined);
    });
});
