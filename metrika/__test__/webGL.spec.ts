import * as chai from 'chai';
import * as sinon from 'sinon';
import * as object from '@src/utils/object';
import * as functionUtils from '@src/utils/function';
import { checkCanvasCtx } from '../webGL';

describe('webGL factor', () => {
    const sandbox = sinon.createSandbox();
    let getPathStub: sinon.SinonStub<any, any>;
    let isNativeStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        getPathStub = sandbox.stub(object, 'getPath');
        isNativeStub = sandbox.stub(functionUtils, 'isNativeFunction');
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('works only with valid canvas', () => {
        const canvasCtx = {} as any;
        const nullResult = checkCanvasCtx({} as any, canvasCtx);
        chai.expect(nullResult).to.be.false;
        sinon.assert.notCalled(getPathStub);
        const floatWin = {
            Float32Array: () => {},
        } as any;
        const floatResult = checkCanvasCtx(floatWin, {} as any);
        chai.expect(floatResult).to.be.false;
        sinon.assert.calledWith(getPathStub, canvasCtx, 'canvas');
    });
    it('checks canvas ok', () => {
        getPathStub.returns({});
        isNativeStub.returns(true);
        const bufferResult = checkCanvasCtx(
            {
                Float32Array: () => {},
            } as any,
            {
                createBuffer: () => {},
            } as any,
        );
        chai.expect(bufferResult).to.be.true;
    });
    it('skips if createBuffer error', () => {
        getPathStub.returns({});
        isNativeStub.returns(true);
        const bufferStub = sinon.stub().throws('wrong!');
        const bufferResult = checkCanvasCtx(
            {
                Float32Array: () => {},
            } as any,
            {
                createBuffer: bufferStub,
            } as any,
        );
        chai.expect(bufferResult).to.be.false;
        sinon.assert.calledOnce(bufferStub);
    });
    it('works only with native fn', () => {
        const toDataURL = {};
        getPathStub.returns({
            toDataURL,
        });
        const nativeResult = checkCanvasCtx(
            {
                Float32Array: () => {},
            } as any,
            {} as any,
        );

        sinon.assert.calledWith(isNativeStub, 'toDataUrl', toDataURL);
        chai.expect(nativeResult).to.be.false;
    });
});
