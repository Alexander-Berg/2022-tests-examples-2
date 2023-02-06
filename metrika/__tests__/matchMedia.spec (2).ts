import * as chai from 'chai';
import * as sinon from 'sinon';
import * as func from '@src/utils/function';
import { QUERY_LIST } from '@src/utils/browser/matchMedia';
import { matchMediaFactor } from '../matchMedia';

describe('match Media Factor', () => {
    const sandbox = sinon.createSandbox();
    let matchMediaStub: sinon.SinonStub<any, any>;
    let isNativeStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        matchMediaStub = sandbox.stub().named('matchMediaStub');
        isNativeStub = sandbox.stub(func, 'isNativeFunction');
        isNativeStub.returns(true);
    });
    afterEach(() => {
        sandbox.resetHistory();
        sandbox.restore();
    });
    it('returns empty string value', () => {
        chai.expect(matchMediaFactor({} as any)).to.be.eq('');
        sinon.assert.notCalled(isNativeStub);
        isNativeStub.returns(false);
        chai.expect(
            matchMediaFactor({
                matchMedia: () => {},
            } as any),
        ).to.be.eq('');
        sinon.assert.calledOnce(isNativeStub);
    });
    it('returns string value', () => {
        const matches = false;
        const stringToQuery = (query: string) => {
            return `${matches}x(${query})`;
        };
        matchMediaStub.callsFake((media) => ({ media, matches }));
        const result = matchMediaFactor({
            matchMedia: matchMediaStub,
        } as any);
        chai.expect(result).to.be.equal(
            QUERY_LIST.map(stringToQuery).join('x'),
        );
    });
});
