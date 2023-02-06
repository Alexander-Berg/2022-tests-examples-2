/**
 * @jest-environment node
 */
import {removeTrailingSlash} from './string';

describe('removeTrailingSlash', () => {
    it('слэш должен убираться с конца', () => expect(removeTrailingSlash('test/')).toBe('test'));
    it('всё остальное должно проходить как есть', () =>
        expect(removeTrailingSlash('test')).toBe('test'));
});
