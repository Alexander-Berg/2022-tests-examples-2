import {convertObjectToArray} from '../convertObjectToArray';

describe('convertObjectToArray tests', () => {
    test('it must return array from object with simple object)', () => {
        const item = {
            0: '42',
            '2': '1',
            '5': '3',
            3: '4',
        };

        expect(convertObjectToArray(item)).toStrictEqual([
            '42',
            undefined,
            '1',
            '4',
            undefined,
            '3',
        ]);
    });

    test('it must return array from object with text in keys)', () => {
        const item = {
            'abc': '42',
            '2': '1',
            '5': '3',
            3: '4',
            'foo_bar': 1,
        };

        expect(convertObjectToArray(item)).toStrictEqual([]);
    });

    test('it must return array from object with custom values)', () => {
        const item = {
            // eslint-disable-next-line @typescript-eslint/no-empty-function
            '2': () => {},
            // eslint-disable-next-line @typescript-eslint/no-empty-function
            '5': [],
            3: class {},
        };

        expect(convertObjectToArray(item)).toStrictEqual([
            undefined,
            undefined,
            item['2'],
            item[3],
            undefined,
            [],
        ]);
    });

    test('it must return array from object with empty object)', () => {
        const item = {};

        expect(convertObjectToArray(item)).toStrictEqual([]);
    });
});
