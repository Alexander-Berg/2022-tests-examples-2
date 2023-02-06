import { omit } from '../omit';

describe('omit', () => {
    it('should return object with keys excluded', () => {
        const obj = { foo: 'Foo', bar: 'Bar', baz: 'Baz' } as const;

        const result = omit(obj, ['foo', 'baz']);

        expect(result).toHaveProperty('bar');
        expect(result).not.toHaveProperty('foo');
        expect(result).not.toHaveProperty('baz');
    });

    it('should return new object', () => {
        const obj = { foo: 'Foo' } as const;

        expect(omit(obj, [])).not.toBe(obj);
    });
});
