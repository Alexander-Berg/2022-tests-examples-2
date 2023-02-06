import {makeKey} from './makeKey';

describe('makeKey', () => {
    test('primitives', () => {
        expect(makeKey(true)).toBe('true');
        expect(makeKey(0)).toBe('0');
        expect(makeKey(undefined)).toBe('undefined');
        expect(makeKey(null)).toBe('null');
        expect(makeKey({})).toBe('{}');
        expect(makeKey([])).toBe('[]');
        expect(makeKey('xxx')).toBe('"xxx"');

        expect(makeKey(true, 0, undefined, null, {}, [], 'xxx')).toBe(
            'true_0_undefined_null_{}_[]_"xxx"',
        );
    });

    test('object keys sorted', () => {
        const key1 = makeKey({
            x: 1,
            b: {
                y: ['a'],
                z: [
                    {
                        a: true,
                    },
                ],
            },
        });

        const key2 = makeKey({
            b: {
                z: [
                    {
                        a: true,
                    },
                ],
                y: ['a'],
            },
            x: 1,
        });

        expect(key1).toBe('{"b":{"y":["a"],"z":[{"a":true}]},"x":1}');
        expect(key1).toBe(key2);
    });

    test('JSON compatible', () => {
        const obj = {
            b: {
                z: [
                    {
                        a: true,
                    },
                ],
                y: [{c: null}, ['a']],
                b: undefined,
            },
            x: 1,
        };

        expect(JSON.parse(makeKey(obj))).toEqual(obj);
        expect(JSON.parse(makeKey(true))).toBe(true);
        expect(JSON.parse(makeKey(0))).toBe(0);
        expect(JSON.parse(makeKey(null))).toBe(null);
        expect(JSON.parse(makeKey({}))).toEqual({});
        expect(JSON.parse(makeKey([]))).toEqual([]);
        expect(JSON.parse(makeKey([1, undefined, 2]))).toEqual([1, 2]);
        expect(JSON.parse(makeKey('xxx'))).toBe('xxx');
    });

    test('function', () => {
        expect(
            makeKey(() => {
                return null;
            }),
        ).toEqual('');
    });
});
