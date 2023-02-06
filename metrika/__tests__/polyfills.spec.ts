import * as chai from 'chai';
import * as Poly from '..';
import { reducePoly } from '../reduce';
import { callPoly, includesPoly } from '..';
import { joinPoly } from '../join';

describe('polyFils should work', () => {
    it('array join', () => {
        chai.expect(joinPoly('123123', [])).to.be.eq('');
        chai.expect(joinPoly('123123', [1])).to.be.eq('1');
        chai.expect(joinPoly('-', [1, 2])).to.be.eq('1-2');
        chai.expect(joinPoly('-', [1, 2, 3])).to.be.eq('1-2-3');
    });
    it('includes checks elem in array', () => {
        chai.expect(includesPoly(1, [1, 2, 3])).to.be.ok;
        chai.expect(includesPoly(4, [1, 2, 3])).to.be.not.ok;
    });
    it('call poly call fns trans args', () => {
        let counter = 0;
        const fn = () => {
            counter += 1;
            return counter;
        };
        let result = callPoly(fn);
        chai.expect(result).to.be.equal(1);
        result = callPoly(fn, [1]);
        chai.expect(result).to.be.equal(2);
        result = callPoly(fn, [1, 1]);
        chai.expect(result).to.be.equal(3);
        result = callPoly(fn, [1, 1, 1]);
        chai.expect(result).to.be.equal(4);
        result = callPoly(fn, [1, 1, 1, 1]);
        chai.expect(result).to.be.equal(5);
    });
    it('reduce trans args', () => {
        const sum = reducePoly(
            (prev: number, next: number) => {
                return prev + next;
            },
            0,
            [2, 2, 2],
        );
        chai.expect(sum).to.be.equal(6);
    });
    it('reduce def args', () => {
        const sum = reducePoly(
            (prev, next) => {
                return prev + next;
            },
            1,
            [2, 2, 2],
        );
        chai.expect(sum).to.be.equal(7);
    });
    it('reduce def index', () => {
        let index = 0;
        const sum = reducePoly(
            (prev, next, i) => {
                index = i;
                return prev + next;
            },
            1,
            [2, 2, 2],
        );
        chai.expect(index).to.be.equal(2);
        chai.expect(sum).to.be.equal(7);
    });
    it('map iterate arrays', () => {
        const result = Poly.mapPoly((i) => i * 2, [1, 2, 3]);
        chai.expect(result).to.be.an('array').that.does.deep.equal([2, 4, 6]);
    });
    it('map send index', () => {
        let index = 0;
        Poly.mapPoly(
            (_, i) => {
                index = i;
                return 1;
            },
            [1, 2, 3],
        );
        chai.expect(index).to.be.equal(2);
    });
    it('entriesPoly ok with undefined', () => {
        const result = Poly.entriesPoly(undefined);
        chai.expect(result).to.have.lengthOf(0);
    });
    it('entriesPoly iterate array', () => {
        const result = Poly.entriesPoly({
            test: 1,
            val: 2,
        });
        chai.expect(result).to.have.lengthOf(2);
        chai.expect(result[0]).to.have.lengthOf(2);
        chai.expect(result[0][0]).to.be.oneOf(['test', 'val']);
        chai.expect(result[1][0]).to.be.oneOf(['test', 'val']);
        chai.expect(result[0][1]).to.be.oneOf([1, 2]);
        chai.expect(result[1][1]).to.be.oneOf([1, 2]);
    });
    it('valuesPoly iterate array', () => {
        const result = Poly.valuesPoly({
            test: 1,
            val: 2,
        });
        chai.expect(result).to.have.lengthOf(2);
        result.forEach((value) => chai.expect(value).to.be.oneOf([1, 2]));
    });
    it('assignPoly copy props', () => {
        const result = Poly.assignPoly(
            {
                info0: 1,
            },
            {
                info1: 2,
                test: 1,
            },
            {
                info3: 3,
                test: 2,
            },
        );
        chai.expect(result.test).to.be.equal(2);
        chai.expect(result.info0).to.be.equal(1);
        chai.expect(result.info1).to.be.equal(2);
        chai.expect(result.info3).to.be.equal(3);
    });
    it('assignPoly handles toString own prop (old IE only)', () => {
        const result = Poly.assignPoly(
            {},
            {
                toString: () => 'hooray',
            },
        );
        chai.expect(`${result}`).to.be.equal('hooray');
    });
    it('keysPoly return obj keys', () => {
        const keys = Poly.keysPoly({
            test: 1,
        });
        chai.expect(keys).to.include('test');
        chai.expect(keys).to.not.include('length');
    });
    it('somePoly', () => {
        chai.expect(Poly.somePoly((el: number) => el > 5, [1, 5, 6, 7])).to.be
            .ok;
        chai.expect(Poly.somePoly((el: number) => el < 0, [1, 5, 6, 7])).to.be
            .not.ok;
    });
    it('findPoly', () => {
        chai.expect(
            Poly.findPoly((el: number) => el > 5, [1, 5, 6, 7]),
        ).to.be.equal(6);
        chai.expect(
            Poly.findPoly((el: number) => el < 0, [1, 5, 6, 7]),
        ).to.be.equal(undefined);
    });
    it('flatMapPoly', () => {
        chai.expect(Poly.flatMapPoly((el: number) => [el], [])).to.deep.equal(
            [],
        );
        chai.expect(
            Poly.flatMapPoly((el: number) => [el, el], [1, 5]),
        ).to.deep.equal([1, 1, 5, 5]);
        chai.expect(
            Poly.flatMapPoly(
                (el: number) => {
                    if (el < 2) {
                        return [];
                    }
                    return [el, el * 2];
                },
                [1, 2, 3],
            ),
        ).to.deep.equal([2, 4, 3, 6]);
        chai.expect(Poly.flatMapPoly((el: number) => el, [1, 2])).to.deep.equal(
            [1, 2],
        );
    });
});
