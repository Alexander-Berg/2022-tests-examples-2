import * as sinon from 'sinon';
import * as dom from '@src/utils/dom';
import * as chai from 'chai';
import { videoFactor } from '../video';

describe('video factor', () => {
    const sandbox = sinon.createSandbox();
    let createElemStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        createElemStub = sandbox.stub(dom, 'getElemCreateFunction');
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('reads non codecs if create is broken', () => {
        createElemStub.returns(null);
        const result = videoFactor({} as any);
        sinon.assert.calledOnce(createElemStub);
        chai.expect(result).to.be.eq('');
    });
    it('reads some codecs', () => {
        const getterStub = sinon.stub();
        const testResult = 12;
        getterStub.callsFake(function a(this: any, arg: string) {
            if (arg.includes(';')) {
                chai.expect(arg).to.include('codecs');
            }
            chai.expect(arg).to.include('/');
            chai.expect(this.test).to.be.eq(1);
            return testResult;
        });
        createElemStub.returns(() => ({
            test: 1,
            canPlayType: getterStub,
        }));
        const result = videoFactor({} as any);
        sinon.assert.called(getterStub);
        chai.expect(result).to.include(testResult);
    });
});
