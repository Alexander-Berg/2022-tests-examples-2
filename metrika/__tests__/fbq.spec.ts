import * as sinon from 'sinon';
import * as chai from 'chai';
import * as defer from '@src/utils/defer';
import { fbqObserver } from '@src/utils/fbq';

describe('fbqObserver', () => {
    const sandbox = sinon.createSandbox();
    const VALID_DATA = ['track', 'Purchase', { currency: 'USD', value: 30.0 }];
    const INVALID_DATA = null;
    const RETURN_DATA = 'return_data';

    let fbqSpy: sinon.SinonSpy;
    let cbSpy: sinon.SinonSpy;

    beforeEach(() => {
        fbqSpy = sandbox.spy(() => RETURN_DATA);
        cbSpy = sandbox.spy();
        (fbqSpy as any).callMethod = () => {};
    });

    afterEach(() => {
        (fbqSpy as any).callMethod = undefined;
        sandbox.restore();
    });

    it('override function', () => {
        const ctxStub = {
            fbq: fbqSpy,
            JSON: window.JSON,
        } as any;
        const args = VALID_DATA;

        fbqObserver(ctxStub, cbSpy);

        ctxStub.fbq(...args);
        ctxStub.fbq(INVALID_DATA);

        sinon.assert.calledTwice(fbqSpy);
        sinon.assert.calledWith(fbqSpy.getCall(0), ...args);
        chai.expect(fbqSpy.getCall(0).returnValue).to.eq(RETURN_DATA);

        sinon.assert.calledWith(fbqSpy.getCall(1), INVALID_DATA);
        chai.expect(fbqSpy.getCall(1).returnValue).to.eq(RETURN_DATA);

        sinon.assert.calledTwice(cbSpy);
        sinon.assert.calledWith(cbSpy.getCall(0), args);
        sinon.assert.calledWith(cbSpy.getCall(1), [INVALID_DATA]);
    });

    it('override function defer', () => {
        const ctxStub = {
            JSON: window.JSON,
        } as any;
        sandbox.stub(defer, 'setDefer').callsFake(((
            ctx: Window,
            fn: Function,
        ) => {
            ctxStub.fbq = fbqSpy;
            fn();
        }) as any);

        fbqObserver(ctxStub, cbSpy);
        ctxStub.fbq(...VALID_DATA);

        sinon.assert.calledOnce(fbqSpy);
        sinon.assert.calledOnce(cbSpy);
    });

    it('call with queue', (done) => {
        const ctxStub = {
            JSON: window.JSON,
            setTimeout: window.setTimeout,
            clearTimeout: window.clearTimeout,
            fbq: { queue: [VALID_DATA] },
        } as any;

        sandbox.stub(defer, 'setDefer').callsFake(((
            ctx: Window,
            fn: Function,
        ) => {
            ctxStub.fbq = {
                ...ctxStub.fbq,
                ...fbqSpy,
            };
            fn();
            done();
        }) as any);

        fbqObserver(ctxStub, cbSpy);

        sinon.assert.calledOnce(fbqSpy);
        sinon.assert.calledWith(fbqSpy.getCall(0), ...VALID_DATA);

        sinon.assert.calledOnce(cbSpy);
        sinon.assert.calledWith(cbSpy.getCall(0), VALID_DATA);
    });
});
