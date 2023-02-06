import { hasOrderedInclusion } from '../utils';

describe('hasOrderedInclusion', () => {
    it('should return true', () => {
        expect(hasOrderedInclusion([['1', '2', '3'], ['1']])).toBeTruthy();
        expect(
            hasOrderedInclusion([
                ['1', '2', '3'],
                ['1', '2'],
            ]),
        ).toBeTruthy();
        expect(
            hasOrderedInclusion([['1', '2', '3'], ['2'], ['3'], ['2', '4']]),
        ).toBeTruthy();
    });

    it('should return false', () => {
        expect(
            hasOrderedInclusion([['1', '2', '3'], ['2'], ['3', '2']]),
        ).toBeFalsy();
        expect(
            hasOrderedInclusion([
                ['1', '2', '3'],
                ['1', '2', '4'],
            ]),
        ).toBeFalsy();
        expect(
            hasOrderedInclusion([
                ['1', '2', '3'],
                ['1', '3'],
                ['4', '2'],
            ]),
        ).toBeFalsy();
    });
});
