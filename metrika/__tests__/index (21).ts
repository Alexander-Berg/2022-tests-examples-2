import { parse, serialize } from '..';

describe('StorageContainer', () => {
    describe('parse', () => {
        it('empty values', () => {
            expect(parse('')).toEqual({});
            expect(parse()).toEqual({});
            expect(parse(null)).toEqual({});
            expect(parse(undefined)).toEqual({});
        });
        it('wrong type values', () => {
            expect(parse(0)).toEqual({});
            expect(parse(1)).toEqual({});
            expect(parse([])).toEqual({});
            expect(parse({})).toEqual({});
        });
        it('wrong format values', () => {
            expect(parse(':')).toEqual({});
            expect(parse('name1')).toEqual({});
            expect(parse('name1:')).toEqual({});
            expect(parse('name1:#')).toEqual({});
            expect(parse('name1:#:')).toEqual({});
        });
        it('encoded values', () => {
            expect(parse('%D0%B0:%D0%B1')).toEqual({ а: 'б' });
        });
    });
    describe('serialize', () => {
        it('works', () => {
            expect(serialize({ a: 1 })).toEqual('a:1');
            expect(serialize({ a: 1, b: 2 })).toEqual('a:1#b:2');
        });
    });
});
