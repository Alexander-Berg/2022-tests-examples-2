import { expect } from 'chai';
import * as def from '@src/utils/defer';
import * as sinon from 'sinon';
import { sendToFrame, getIframeState } from '../iframeConnector';

describe('iframeConnector', () => {
    const sandbox = sinon.createSandbox();
    let serialiseStub: sinon.SinonStub<any, any>;
    let deferStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        deferStub = sandbox.stub(def, 'setDefer');
        serialiseStub = sandbox.stub();
        serialiseStub.returns({
            meta: {},
        });
    });
    afterEach(() => {
        sandbox.reset();
        sandbox.restore();
    });
    it('set defer if everything is ok', () => {
        const postMessageStub = sandbox.stub();
        const win = {} as any;
        const iframeCtx = {
            postMessage: postMessageStub,
        } as any;
        deferStub.callsFake((ctx: any, cb) => {
            expect(ctx).to.be.eq(win);
            cb();
            const state = getIframeState(win);
            expect(state.pending).to.be.empty;
        });
        const result = sendToFrame(win, serialiseStub, iframeCtx, {}, () => {});
        expect(result).to.be.undefined;
        sinon.assert.calledOnce(postMessageStub);
        sinon.assert.calledOnce(deferStub);
    });
    it('call postMessage in sendToFrame', () => {
        const iframeCtx = {
            postMessage: sandbox.stub().throws('Broken post'),
        } as any;
        const result = sendToFrame(
            {} as any,
            serialiseStub,
            iframeCtx,
            {},
            () => {},
        );
        expect(result).to.be.undefined;
        sinon.assert.notCalled(deferStub);
    });
    it('return not ok if iframe ctx empty', () => {
        const iframeCtx = {} as any;
        const result = sendToFrame(
            {} as any,
            serialiseStub,
            iframeCtx,
            {},
            () => {},
        );
        expect(result).to.be.undefined;
        sinon.assert.notCalled(deferStub);
    });
});
