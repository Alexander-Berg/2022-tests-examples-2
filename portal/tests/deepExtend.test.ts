import { deepExtend } from '../deepExtend';

describe('deepExtend', function() {
    test('should extend', function() {
        expect(deepExtend({}, { abc: 123 })).toEqual({ abc: 123 });
    });

    test('should return base', function() {
        let base = {};
        expect(deepExtend(base, { abc: 123 })).toEqual(base);
    });

    test('should override props', function() {
        let base = {
            abc: 456
        };
        expect(deepExtend(base, { abc: 123, def: true })).toEqual({ abc: 123, def: true });
    });

    test('should extend inner arrays', function() {
        expect(deepExtend({}, { a: [1, 2, 3] })).toEqual({ a: [1, 2, 3] });

        let base = { a: [4, 5, 6], b: 7 };
        let extender = { a: [1, 2, 3] };
        expect(deepExtend(base, extender)).toEqual({ b: 7, a: [1, 2, 3] });
        expect(deepExtend(base, extender).a).toEqual(extender.a);
        expect(deepExtend(base, extender).a).not.toBe(extender.a);

        expect(deepExtend({ a: [1, 2, 3] }, { a: [4] })).toEqual({ a: [4, 2, 3] });
        expect(deepExtend({ a: [1, 2, 3] }, { a: [{ b: 7 }] })).toEqual({ a: [{ b: 7 }, 2, 3] });
        expect(deepExtend(
            { a: [{ b: 4, c: 5 }, 2, 3] },
            { a: [{ b: 7, d: 8 }] }
        )).toEqual({ a: [{ b: 7, c: 5, d: 8 }, 2, 3] });
    });

    test('should extend inner objects', function() {
        let extender = {
            a: {
                b: true
            }
        };
        let res = deepExtend({}, extender);
        expect(res).toEqual({ a: { b: true } });
        expect(res.a).not.toBe(extender.a);
        expect(res.a).toEqual(extender.a);
    });

    test('should extend inner dates and functions', function() {
        let base = {
            a: {
                c: 123
            }
        };
        let extender = {
            a: {
                b: true
            },
            d: new Date(),
            e: () => {}
        };
        let res = deepExtend(base, extender);
        expect(res).toEqual({
            a: {
                b: true,
                c: 123
            },
            d: extender.d,
            e: extender.e
        });
    });

    test('should extend with null', function() {
        let base = {
            abc: 123,
            def: 456
        };

        deepExtend(base, { abc: null });

        expect(base).toEqual({
            abc: null,
            def: 456
        });
    });

    test('should not process __proto__', function() {
        let base = {
            abc: 123,
            def: 456
        };

        let extended = Object.create(base);

        extended.foo = 789;

        deepExtend(extended, JSON.parse('{"__proto__": {"extra": "new"}}'));

        expect(base).toEqual({
            abc: 123,
            def: 456
        });
    });
});
