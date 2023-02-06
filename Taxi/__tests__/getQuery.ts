import {getQuery} from '../getQuery';

describe('getQuery', () => {
    it('должен преобразовывать строку, с ведущим "?", в объект', () => {
        expect(getQuery('?a=1&b=2')).toEqual({
            a: '1',
            b: '2',
        });
    });
    it('должен преобразовывать строку, без ведущего "?", в объект', () => {
        expect(getQuery('a=1&b=2')).toEqual({
            a: '1',
            b: '2',
        });
    });
    it('должен возвращать пустой объект, если ничего не передали', () => {
        expect(getQuery()).toEqual({});
        expect(getQuery(null as any)).toEqual({});
        expect(getQuery(undefined)).toEqual({});
    });
    it('должен приводить ключи к нижнему регистру', () => {
        expect(getQuery('AAA=1')).toEqual({
            aaa: '1',
        });
        expect(getQuery('?AAA=1&bbB=2')).toEqual({
            aaa: '1',
            bbb: '2',
        });
    });
    it('должен валидно обрабатывать закодированный урл', () => {
        expect(getQuery('?a=%2B%2B%2B')).toEqual({
            a: '+++',
        });
    });
});
