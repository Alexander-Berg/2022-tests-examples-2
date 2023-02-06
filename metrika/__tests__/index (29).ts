import { range, identity } from 'lodash';
import { camelCase } from '..';

function getPlainObject() {
    return { some_id: 1, some_name: 'hi' };
}

function getDeepObject() {
    return {
        some_id: 1,
        some_name: 'hi',
        some_chld: { some_chld: { some_chld: 'sub_hi' } },
    };
}

function getArray(start: number, end: number, fn: any) {
    return range(start, end).map(fn);
}

function getSearchParams() {
    return new URLSearchParams('some_id=1&some_name=2');
}

describe('camelCase', () => {
    it('one level simple object', () => {
        const result = camelCase(getPlainObject());
        expect(result).toMatchSnapshot();
    });
    it('deep object', () => {
        const obj = getDeepObject();
        const result = camelCase(obj);

        expect(result).toMatchSnapshot();
    });
    it('simple array', () => {
        const array = getArray(1, 5, identity);
        const result = camelCase(array);

        expect(result).toMatchSnapshot();
    });
    it('array with simple objects', () => {
        const array = getArray(1, 5, getPlainObject);
        const result = camelCase(array);

        expect(result).toMatchSnapshot();
    });
    it('array with deep objects', () => {
        const array = getArray(1, 5, getDeepObject);
        const result = camelCase(array);

        expect(result).toMatchSnapshot();
    });
    it(`doesn't mutate original object`, () => {
        const objectLike = getPlainObject();
        const objectLikeResult = camelCase(objectLike);

        expect(objectLike !== objectLikeResult).toBeTruthy();

        const objectLikeDeep = getDeepObject();
        const objectLikeDeepResult = camelCase(objectLike);

        expect(objectLikeDeep !== objectLikeDeepResult).toBeTruthy();

        const arrayLike = [1, 2, 3, 4, 5];
        const arrayLikeResult = camelCase(arrayLike);

        expect(arrayLike !== arrayLikeResult).toBeTruthy();
    });
    it('URLSearchParams', () => {
        const params = getSearchParams();
        expect(camelCase(params).toString()).toMatchSnapshot();
    });
    it(`doesn't mutate original URLSearchParams instance`, () => {
        const params = getSearchParams();
        const processedParams = camelCase(params);

        expect(params !== processedParams).toBeTruthy();
    });
});
