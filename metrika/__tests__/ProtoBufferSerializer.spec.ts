// import * as dConsole from '@src/providers/debugConsole';
import * as time from '@src/utils/time';
import * as chai from 'chai';
import * as sinon from 'sinon';
import * as generated from '@generated/proto/recorder_proto';
import * as debug from '@src/providers/debugConsole';
import * as writer from '@src/utils/proto/writer';
import * as async from '@src/utils/async';
import { expect } from 'chai';
import { ProtoBufferSerializer } from '../ProtoBufferSerializer';

describe('ProtoBufferSerializer universal', () => {
    const testSize = 42;
    const win: Window = {
        // eslint-disable-next-line no-restricted-globals
        isNaN,
        Uint8Array,
        Math,
        Blob: function a() {
            this.size = testSize;
        },
    } as any as Window;
    const sandbox = sinon.createSandbox();
    const startTime = 560;
    let getLengthStub: sinon.SinonStub<any, any>;
    let getByteStub: sinon.SinonStub<any, any>;
    const iteratorSpy = [sandbox.spy()];
    const fnList: Function[] = [];
    const addFnToFnList = (fn: Function) => {
        fnList.push(fn);
        return addFnToFnList;
    };
    beforeEach(() => {
        getLengthStub = sandbox.stub(writer, 'protoPrepareLength');
        iteratorSpy[0].resetHistory();
        getByteStub = sandbox.stub(writer, 'protoWriteBytes');
        sandbox.stub(async, 'taskChain').callsFake((fn) => fn(iteratorSpy));
        sandbox.stub(async, 'executeIterator').returns(addFnToFnList as any);
        sandbox.stub(time, 'TimeOne').returns((fn) => fn({} as any));
        sandbox.stub(time, 'getFromStart').returns(startTime);
        sandbox.stub(debug, 'debugEnabled').returns({
            isDebug: true,
            isEnabled: false,
            hasCookieFlag: false,
        });
    });
    afterEach(() => {
        fnList.splice(0, fnList.length);
        sandbox.restore();
    });
    it('imports serializer and call size and write fn', () => {
        getLengthStub.returns(iteratorSpy[0]);
        const seri = new ProtoBufferSerializer(win);
        const testType = 'testType';
        const testData = {
            testArray: [1, 2, 3, 4, null],
            testObj: {
                a: 1,
                b: undefined,
            },
            testField: 1,
            nullField: null,
        };
        const testObj = {
            type: testType,
            data: testData,
        };
        chai.expect(seri).to.be.ok;
        seri.serializeData(testObj);
        sinon.assert.calledWith(getLengthStub, win, generated.encodeWrapper);
        sinon.assert.calledOnce(iteratorSpy[0]);
        const serializeData = [42];
        chai.expect(seri.getRequestBodySize(serializeData as any)).to.be.equal(
            testSize,
        );
        chai.expect(seri.splitToChunks(serializeData as any)).to.be.deep.equal([
            serializeData,
        ]);
        getLengthStub.returns((fn: any) => {
            fn(iteratorSpy);
        });
        seri.serialize([testObj]);
        sinon.assert.calledWith(getLengthStub, win, generated.encodeWrapper);
        sinon.assert.calledWith(getByteStub, win, iteratorSpy);
    });
    it('checks window features in method check', () => {
        const testWin = {
            Uint8Array: {
                prototype: { slice: 1 },
            },
            Blob: function a() {
                this.size = 2;
            },
        } as any as Window;
        const seri = new ProtoBufferSerializer(testWin);
        expect(seri.isEnabled()).to.be.ok;
        const emptyWinResult = new ProtoBufferSerializer({} as any);
        expect(emptyWinResult.isEnabled()).to.be.not.ok;
    });
});
