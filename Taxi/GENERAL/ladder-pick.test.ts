import {describe, expect, it} from 'tests/jest.globals';

import ladderPick from './ladder-pick';

const iterations = 10;

const getIterationResult = (getItem: () => string, itemsCount: number) => {
    const result = [];
    for (let i = 0; i < itemsCount; i++) {
        result.push(getItem());
    }
    return result.join('');
};

describe('ladderPick', () => {
    it('should return correct value (height=3)', async () => {
        const getItem = ladderPick(['a', 'b', 'c', 'd', 'e', 'f'], 3);

        const expectedIterationResult = 'bcefcf';
        for (let i = 0; i < iterations; i++) {
            const result = getIterationResult(getItem, expectedIterationResult.length);
            expect(result).toBe(expectedIterationResult);
        }
    });

    it('should return correct value (height=3, inverse)', async () => {
        const getItem = ladderPick(['a', 'b', 'c', 'd', 'e', 'f'], 3, true);

        const expectedIterationResult = 'abdead';
        for (let i = 0; i < iterations; i++) {
            const result = getIterationResult(getItem, expectedIterationResult.length);
            expect(result).toBe(expectedIterationResult);
        }
    });

    it('should return correct value (height=4)', async () => {
        const getItem = ladderPick(['a', 'b', 'c', 'd', 'e', 'f'], 4);

        const expectedIterationResult = 'bcdfcdd';
        for (let i = 0; i < iterations; i++) {
            const result = getIterationResult(getItem, expectedIterationResult.length);
            expect(result).toBe(expectedIterationResult);
        }
    });

    it('should return correct value (height=4, inverse)', async () => {
        const getItem = ladderPick(['a', 'b', 'c', 'd', 'e', 'f'], 4, true);

        const expectedIterationResult = 'abcefabefae';
        for (let i = 0; i < iterations; i++) {
            const result = getIterationResult(getItem, expectedIterationResult.length);
            expect(result).toBe(expectedIterationResult);
        }
    });

    it('should return correct value (height=5)', async () => {
        const getItem = ladderPick(['a', 'b', 'c', 'd', 'e', 'f'], 5);

        const expectedIterationResult = 'bcdecdedee';
        for (let i = 0; i < iterations; i++) {
            const result = getIterationResult(getItem, expectedIterationResult.length);
            expect(result).toBe(expectedIterationResult);
        }
    });

    it('should return correct value (height=5, inverse)', async () => {
        const getItem = ladderPick(['a', 'b', 'c', 'd', 'e', 'f'], 5, true);

        const expectedIterationResult = 'abcdfabcfabfaf';
        for (let i = 0; i < iterations; i++) {
            const result = getIterationResult(getItem, expectedIterationResult.length);
            expect(result).toBe(expectedIterationResult);
        }
    });
});
