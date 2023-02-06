import * as chai from 'chai';
import * as native from '@src/utils/function/isNativeFunction/toNativeOrFalse';
import * as sinon from 'sinon';
import {
    exclude,
    isArray,
    getRange,
    toArray,
    cSome,
    cFind,
    flatMap,
    includes,
} from '..';
import { reversePoly } from '../reverse';
// @ts-ignore
import { isArrayFn, isArrayPolyfil } from '../isArray';

describe('Array utils', () => {
    const sandbox = sinon.createSandbox();
    beforeEach(() => {
        // @ts-expect-error
        isArrayFn = undefined as any;
        sandbox
            .stub(native, 'toNativeOrFalse')
            .callsFake(((a: any) => a) as any);
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('isArray Polyfil', () => {
        chai.expect(isArrayPolyfil([])).to.be.true;
        chai.expect(isArrayPolyfil({ length: 10 })).to.be.false;
    });
    it('isArray', () => {
        chai.expect(isArray([])).to.be.true;
        chai.expect(isArray({ length: 10 })).to.be.false;
    });
    it('exclude', () => {
        chai.expect(exclude(['a', 'b', 'c'], ['a', 'b'])).to.deep.equal(['c']);
    });

    it('getRange', () => {
        chai.expect(getRange(3)).to.deep.equal([0, 1, 2, 3]);
        chai.expect(getRange(-1)).to.deep.equal([]);
    });

    it('toArray', () => {
        const set = new Set();
        set.add(1);
        set.add(2);
        chai.expect(toArray(set)).to.deep.equal([1, 2]);
        chai.expect(toArray({ 0: 'a', 1: 'b', length: 2 })).to.deep.equal([
            'a',
            'b',
        ]);
        chai.expect(toArray(null)).to.deep.equal([]);
    });
    it('cSome', () => {
        chai.expect(cSome((el: number) => el > 5, [1, 5, 6, 7])).to.be.ok;
        chai.expect(cSome((el: number) => el < 0, [1, 5, 6, 7])).to.be.not.ok;
    });
    it('cFind', () => {
        chai.expect(cFind((el: number) => el > 5, [1, 5, 6, 7])).to.be.equal(6);
        chai.expect(cFind((el: number) => el < 0, [1, 5, 6, 7])).to.be.equal(
            undefined,
        );
    });
    it('cFind', () => {
        chai.expect(cFind((el: number) => el > 5, [1, 5, 6, 7])).to.be.equal(6);
        chai.expect(cFind((el: number) => el < 0, [1, 5, 6, 7])).to.be.equal(
            undefined,
        );
    });
    it('flatMap', () => {
        chai.expect(flatMap((el: number) => [el], [])).to.deep.equal([]);
        chai.expect(flatMap((el: number) => [el, el], [1, 5])).to.deep.equal([
            1, 1, 5, 5,
        ]);
        chai.expect(
            flatMap(
                (el: number) => {
                    if (el < 2) {
                        return [];
                    }
                    return [el, el * 2];
                },
                [1, 2, 3],
            ),
        ).to.deep.equal([2, 4, 3, 6]);
        chai.expect(flatMap((el: number) => el, [1, 2])).to.deep.equal([1, 2]);
    });
    it('includes', () => {
        chai.expect(includes(1, [12, 2, 1])).to.be.ok;
        chai.expect(includes(9, [12, 2, 1])).to.be.not.ok;
    });
    it('reverse', () => {
        chai.expect(reversePoly([1, 2, 3])).to.deep.equal([3, 2, 1]);
    });
});
