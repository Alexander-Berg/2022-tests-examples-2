import { copyProps } from '../copyProps';

describe('home.copyProps', function() {
    test('should copy simple value', function() {
        expect(copyProps('str', 1)).toEqual('str');
        expect(copyProps(123, 1)).toEqual(123);
        expect(copyProps(true, 1)).toEqual(true);
    });

    test('should copy array', function() {
        expect(copyProps(['str', 'baz'], [1])).toEqual(['str', 'baz']);
        expect(copyProps([123, 'baz'], [1])).toEqual([123, 'baz']);
    });

    test('should copy object', function() {
        expect(copyProps({
            a: 1,
            b: 2,
            c: 3,
            d: 4
        }, {
            a: 1,
            d: 1
        })).toEqual({ a: 1, d: 4 });
    });

    test('should copy complex data', function() {
        expect(copyProps([{
            a: 1,
            b: 2,
            c: 3,
            d: [4, 5],
            e: {
                a: 6,
                b: 7,
                c: 8,
                d: 9
            },
            f: [{
                a: 10,
                b: 11,
                c: 12,
                d: 13
            }, {
                b: 14,
                c: 15,
                d: 16
            }]
        }, {
            a: 17,
            c: 19,
            d: [20],
            e: {
                a: 22,
                c: 24,
                d: 25
            },
            f: [{
                c: 28,
                d: 29
            }, {
                b: 30,
                d: 32
            }]
        }], [{
            a: 1,
            b: 1,
            d: [1],
            e: {
                a: 1,
                b: 1,
                c: 1
            },
            f: [{
                a: 1,
                c: 1
            }]
        }])).toEqual([{
            a: 1,
            b: 2,
            d: [4, 5],
            e: {
                a: 6,
                b: 7,
                c: 8
            },
            f: [{
                a: 10,
                c: 12
            }, {
                c: 15
            }]
        }, {
            a: 17,
            d: [20],
            e: {
                a: 22,
                c: 24
            },
            f: [{
                c: 28
            }, {
            }]
        }]);
    });

    test('should work with incorrect types', function() {
        // @ts-expect-error incorrect args
        expect(copyProps({
            a: 1,
            b: 2,
            c: 3,
            d: 4
        }, 1)).toBeUndefined();

        // @ts-expect-error incorrect args
        expect(copyProps({
            a: 1,
            b: 2,
            c: 3,
            d: 4
        }, [1])).toEqual([]);

        // @ts-expect-error incorrect args
        expect(copyProps([1, 2, 3], { a: 1 })).toEqual({});

        expect(copyProps({
            a: [1, 2, 3]
        }, {
            a: 1
        })).toEqual({});
    });
});
