import {describe, expect, it} from 'tests/jest.globals';

import circlePick from './circle-pick';

const iterations = 10;

const getIterationResult = (getItem: () => string, itemsCount: number) => {
    const result = [];
    for (let i = 0; i < itemsCount; i++) {
        result.push(getItem());
    }
    return result.join('');
};

describe('circlePick', () => {
    it('should return correct value', async () => {
        const getItem = circlePick(['a', 'b', 'c']);

        const expectedIterationResult = 'abc';
        for (let i = 0; i < iterations; i++) {
            const result = getIterationResult(getItem, expectedIterationResult.length);
            expect(result).toBe(expectedIterationResult);
        }
    });
});
