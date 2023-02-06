import diff from '../diffUtil';

const createDiffObj = <T>(removed: T[], added: T[]) => ({added, removed});

describe('diffUtil', () => {
    it('a,b vs a,b', () => {
        const s1 = ['a', 'b'];
        const s2 = ['a', 'b'];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([], []));
    });

    it('a,b vs b,a', () => {
        const s1 = ['a', 'b'];
        const s2 = ['b', 'a'];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([1], [0]));
    });

    it('a vs a,b', () => {
        const s1 = ['a'];
        const s2 = ['a', 'b'];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([], [1]));
    });

    it('b vs a,b', () => {
        const s1 = ['b'];
        const s2 = ['a', 'b'];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([], [0]));
    });

    it('a,b vs a', () => {
        const s1 = ['a', 'b'];
        const s2 = ['a'];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([1], []));
    });

    it('a,b vs b', () => {
        const s1 = ['a', 'b'];
        const s2 = ['b'];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([0], []));
    });

    it('a,b vs -', () => {
        const s1 = ['a', 'b'];
        const s2: string[] = [];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([0, 1], []));
    });

    it('- vs a,b', () => {
        const s1: string[] = [];
        const s2 = ['a', 'b'];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([], [0, 1]));
    });

    it('a vs b', () => {
        const s1 = ['a'];
        const s2 = ['b'];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([0], [0]));
    });

    it('a,1,b,2 vs c,d,1,2', () => {
        const s1 = ['a', '1', 'b', '2'];
        const s2 = ['c', 'd', '1', '2'];
        expect(diff(s1, s2)).toStrictEqual(createDiffObj([0, 2], [0, 1]));
    });
});
