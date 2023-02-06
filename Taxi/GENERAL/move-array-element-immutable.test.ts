import moveArrayElementImmutable from './move-array-element-immutable';

describe('move array element in immutable way', () => {
    test('it should be immutable', () => {
        const source = [1, 2, 3, 4, 5];
        const moved = moveArrayElementImmutable(source, 0, 0);
        expect(source).toEqual(moved);
        expect(source).not.toBe(moved);
    });

    test('it should move elements', () => {
        const source = [1, 2, 3, 4, 5];
        expect(moveArrayElementImmutable(source, 0, 1)).toEqual([2, 1, 3, 4, 5]);
        expect(moveArrayElementImmutable(source, 2, 0)).toEqual([3, 1, 2, 4, 5]);
        expect(moveArrayElementImmutable(source, 0, 100)).toEqual([2, 3, 4, 5, 1]);
        expect(moveArrayElementImmutable(source, 4, -100)).toEqual([5, 1, 2, 3, 4]);
        expect(moveArrayElementImmutable([], 100, 500)).toEqual([]);
        expect(moveArrayElementImmutable(source, 100, 0)).toEqual(source);
        expect(moveArrayElementImmutable(source, -100, 0)).toEqual(source);
    });
});
