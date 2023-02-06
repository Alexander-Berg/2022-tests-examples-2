import * as sinon from 'sinon';
import { expect } from 'chai';
import * as obj from '@src/utils/object';
import { getBroUid } from '../broUid';

describe('getBroUid', () => {
    const sandbox = sinon.createSandbox();
    let isFunctStub: sinon.SinonStub<any, any>;
    let getPathStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        isFunctStub = sandbox.stub(obj, 'isFunction');
        getPathStub = sandbox.stub(obj, 'getPath');
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('returns null if ctx is empty', () => {
        isFunctStub.returns(false);
        getPathStub.returns(null);
        const result = getBroUid({});
        expect(result).to.be.null;
    });
    it('returns some from ctx methot with rigth context', () => {
        isFunctStub.returns(true);
        const testString = 'hi';
        const result = getBroUid({
            yandex: {
                ctxIn: true,
                getSiteUid() {
                    expect(this.ctxIn).to.be.ok;
                    return testString;
                },
            },
        });
        expect(result).to.be.eq(testString);
    });
});
