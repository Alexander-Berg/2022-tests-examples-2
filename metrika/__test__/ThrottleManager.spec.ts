import * as sinon from 'sinon';
import * as chai from 'chai';
import * as defer from '@src/utils/defer';
import * as time from '@src/utils/time';
import { ThrottleManager } from '../ThrottleManager';

describe('ThrottleManager', () => {
    const sandbox = sinon.createSandbox();
    let setDeferStub: sinon.SinonStub<any, any>;
    let clearDeferStub: sinon.SinonStub<any, any>;
    let stamp = 100;
    const fakeTime: any = () => stamp;
    beforeEach(() => {
        setDeferStub = sandbox.stub(defer, 'setDefer').returns(123);
        clearDeferStub = sandbox.stub(defer, 'clearDefer');
        sandbox.stub(time, 'TimeOne').returns(fakeTime);
    });

    afterEach(() => {
        stamp = 100;
        sandbox.restore();
    });

    it('Creates throttled handler and without first call', () => {
        const fakeCtx: any = {
            Array,
        };
        const manager = new ThrottleManager(fakeCtx);

        const originalFunction = sinon.stub();
        const throttledFunction = manager.createThrottledFunction(
            originalFunction,
            200,
            { firstCall: false },
        );
        throttledFunction(1);
        sinon.assert.notCalled(originalFunction);

        stamp = 300;
        throttledFunction(2);
        sinon.assert.calledWith(clearDeferStub, fakeCtx, 123);
        const [ctx, callback, timeout] = setDeferStub.getCall(1).args;
        chai.expect(ctx).to.equal(fakeCtx);
        chai.expect(timeout).to.equal(200);
        callback();
        sinon.assert.calledWith(originalFunction, 2);

        throttledFunction(3);
        manager.flush();
        sinon.assert.calledWith(originalFunction, 3);
    });

    it('Creates throttled handler and makes first call', () => {
        const fakeCtx: any = {
            Array,
        };
        const manager = new ThrottleManager(fakeCtx);

        const originalFunction = sinon.stub();
        const throttledFunction = manager.createThrottledFunction(
            originalFunction,
            200,
            { firstCall: true },
        );
        throttledFunction(1);
        sinon.assert.calledWith(originalFunction, 1);
        originalFunction.resetHistory();

        const [ctx, callback, timeout] = setDeferStub.getCall(0).args;
        chai.expect(ctx).to.equal(fakeCtx);
        chai.expect(timeout).to.equal(200);

        throttledFunction(2);
        sinon.assert.notCalled(originalFunction);

        stamp = 200;
        callback();
        sinon.assert.notCalled(originalFunction);
    });
});
