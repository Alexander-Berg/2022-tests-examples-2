import * as sinon from 'sinon';
import { expect } from 'chai';
import * as numberUtils from '@src/utils/number';
import { encodeWithSum } from '../utils';
import { tests } from './encoderMap.json';

describe('utils for isp', () => {
    const win = {} as Window;
    const sandbox = sinon.createSandbox();
    let getRandomStub: sinon.SinonStub<
        Parameters<typeof numberUtils.getRandom>,
        any // Long masks are coerced to MAX_INT for too large values. Thus avoid numbers.
    >;

    beforeEach(() => {
        getRandomStub = sandbox.stub(numberUtils, 'getRandom');
    });

    afterEach(() => {
        sandbox.restore();
    });

    describe(`encodeWithSum`, () => {
        it('returns a numeric mask with the same length as uid', () => {
            tests.forEach(({ uid, mask, maskedUid }) => {
                getRandomStub.returns(mask);
                const result = encodeWithSum(win, uid);
                expect(result[0]).to.be.eq(mask);
            });
        });

        it('returns encoded uid', () => {
            tests.forEach(({ uid, mask, maskedUid }) => {
                getRandomStub.returns(mask);
                const result = encodeWithSum(win, uid);
                expect(result[1]).to.be.eq(maskedUid);
            });
        });
    });
});
