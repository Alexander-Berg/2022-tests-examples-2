import * as crossUtils from '@src/middleware/crossDomain/utils';
import * as browserUtils from '@src/utils/browser';
import * as store from '@src/storage/localStorage';
import * as defer from '@src/utils/defer';
import { expect } from 'chai';
import * as sinon from 'sinon';
import {
    asyncFingerPrint,
    asyncFingerPrintSaver,
    ASYNC_FP_KEY,
} from '../asyncFingerPrint';

describe('asyncFingerPrint/asyncFingerPrintSaver', () => {
    const sandbox = sinon.createSandbox();
    let isITPDisabledStub: sinon.SinonStub<any, any>;
    let isFFStub: sinon.SinonStub<any, any>;
    let storeStub: sinon.SinonStub<any, any>;
    let runAsyncStub: sinon.SinonStub<any, any>;
    let win: any;
    const testVal = '123123';
    let getVal: sinon.SinonStub<any, any>;
    let setVal: sinon.SinonStub<any, any>;
    let lsStub: {
        getVal: sinon.SinonStub<any, any>;
        setVal: sinon.SinonStub<any, any>;
    };
    beforeEach(() => {
        win = {};
        getVal = sandbox.stub();
        setVal = sandbox.stub();
        lsStub = {
            getVal,
            setVal,
        };
        isITPDisabledStub = sandbox.stub(crossUtils, 'isITPDisabled');
        isITPDisabledStub.returns(false);
        storeStub = sandbox.stub(store, 'globalLocalStorage');
        storeStub.returns(lsStub);
        isFFStub = sandbox.stub(browserUtils, 'isFF');
        runAsyncStub = sandbox.stub(defer, 'setDefer');
        isFFStub.returns(false);
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('add result data', () => {
        const testArr: string[] = [];
        const expectResult = '7';
        asyncFingerPrintSaver(lsStub as any, testArr, [true, true]);
        expect(testArr).to.be.deep.eq([expectResult]);
        sinon.assert.calledOnceWithExactly(setVal, ASYNC_FP_KEY, expectResult);
    });
    it('ignore emplty result', () => {
        const testArr: string[] = [];
        asyncFingerPrintSaver(lsStub as any, testArr, undefined);
        expect(testArr).to.be.empty;
        sinon.assert.notCalled(setVal);
    });
    it('calls run async', () => {
        const result = asyncFingerPrint(win);
        sinon.assert.calledOnce(runAsyncStub);
        expect(result).to.be.empty;
    });
    it('get value from ls', () => {
        getVal.returns(testVal);
        const result = asyncFingerPrint(win);
        sinon.assert.calledOnceWithExactly(storeStub, win);
        expect(result).to.be.deep.eq([testVal]);
        sinon.assert.notCalled(runAsyncStub);
    });
    it('disabled for ff', () => {
        isITPDisabledStub.returns(true);
        isFFStub.returns(false);
        const result = asyncFingerPrint(win);
        sinon.assert.notCalled(storeStub);
        expect(result).to.be.empty;
        sinon.assert.notCalled(runAsyncStub);
    });
    it('disabled for ITP', () => {
        isITPDisabledStub.returns(true);
        const result = asyncFingerPrint(win);
        sinon.assert.notCalled(storeStub);
        expect(result).to.be.empty;
        sinon.assert.notCalled(runAsyncStub);
    });
});
