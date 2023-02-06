import * as sinon from 'sinon';
import * as writer from '@src/utils/proto/writer';
import * as async from '@src/utils/async';
import { noop } from '@src/utils/function';
import { expect } from 'chai';
import { encodeEventType } from '@generated/proto/event_types';
import { Visor2ProtoBufferSerializer } from '../Visor2ProtoBufferSerializer';

describe('Visor2ProtoBufferSerializer', () => {
    const sandbox = sinon.createSandbox();
    const ctxWin = {
        Array,
    } as any as Window;
    const bufferWrapperFinish = sandbox.spy();
    const testInner = [1, 23, 21, 9, 4, 2];
    const testData = {
        type: 'page',
        data: testInner,
        stamp: 1,
        end: false,
        someRandom: 123123,
    };
    let iterStub: sinon.SinonStub<any, any>;
    let mapStub: sinon.SinonStub<any, any>;
    let execStub: sinon.SinonStub<any, any>;
    let serializer: any;
    let getLengthStub: sinon.SinonStub<any, any>;
    let getByteStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        getLengthStub = sandbox.stub(writer, 'protoPrepareLength');
        getByteStub = sandbox.stub(writer, 'protoWriteBytes');
        iterStub = sandbox.stub(async, 'iterForOf');
        sandbox.stub(async, 'taskChain').callsFake((fn) => fn);
        execStub = sandbox.stub(async, 'executeIterator');
        mapStub = sandbox.stub(async, 'taskMap');
        serializer = new Visor2ProtoBufferSerializer(ctxWin);
    });

    afterEach(() => {
        sandbox.restore();
        bufferWrapperFinish.resetHistory();
    });

    it('throw unexpected event type', () => {
        const typeName = 'test';
        const fn = () =>
            serializer.eventSerializer({
                type: typeName,
            });
        expect(fn).to.throw(`vem.${typeName}`);
    });

    it('serialize repeated event', () => {
        const typeName = 'keystroke';
        const meta = [1, 2, 3];
        const { event } = serializer.eventSerializer({
            type: typeName,
            meta,
        });
        expect(serializer.isSync).to.be.not.ok;
        expect(event.type).to.be.eq(encodeEventType.keystroke);
        expect(event.keystrokesEvent.keystrokes).to.be.deep.eq(meta);
    });
    it('become sync after eof event', () => {
        const typeName = 'eof';
        const { event } = serializer.eventSerializer({
            type: typeName,
            meta: true,
        });
        expect(serializer.isSync).to.be.ok;
        expect(event.type).to.be.eq(encodeEventType.eof);
        expect(event.windowEvent).to.be.ok;
    });
    it('collects async tasks', () => {
        const iterators: Function[] = [];
        const testFn = (fn: Function) => {
            // mapStub result
            if (fn === noop) {
                return noop;
            }
            iterators.push(fn);
            return testFn;
        };
        execStub.returns(testFn);
        const funcList: Function[] = [];
        const tasks = serializer.currentTaskIterList;
        const testRes = 1;
        mapStub.callsFake((fn) => {
            funcList.push(fn);
            if (funcList.length === 1) {
                expect(tasks).to.be.lengthOf(1);
                const res = fn([testRes]);
                expect(tasks).to.be.lengthOf(0);
                iterators.forEach((iterFn) => {
                    iterFn([]);
                });
                expect(tasks).to.be.lengthOf(2);
                expect(res).to.be.eq(testRes);
                sinon.assert.calledOnce(getLengthStub);
                sinon.assert.calledOnce(getByteStub);
            }
            return noop;
        });
        serializer.serialize([testData]);
        serializer.serialize([testData]);
        expect(tasks).to.be.lengthOf(3);
        const typeName = 'eof';
        serializer.eventSerializer({
            type: typeName,
            meta: true,
        });
    });
    it('serialize async', () => {
        const iterators: Function[] = [];
        const testFn = (fn: Function) => {
            iterators.push(fn);
            return testFn;
        };
        execStub.returns(testFn);
        iterStub.callsFake((data, fn) => {
            expect(data).to.be.deep.eq([testData]);
            const result = fn(testData);
            expect(result.data).to.be.deep.eq({
                page: testInner,
            });
            expect(result.stamp).to.be.eq(testData.stamp);
            expect(result.end).to.be.eq(testData.end);
            expect(result.someRandom).to.be.not.eq(testData.someRandom);
            const secondData = {
                partNum: 1,
                data: testInner,
            };
            const result2 = fn(secondData);
            expect(result2.page).to.be.eq(secondData.partNum);
            expect(result2.chunk).to.be.deep.eq(testInner);
            expect(result2.data).to.be.undefined;
        });
        mapStub.callsFake(() => {
            iterators.forEach((fn) => {
                fn([]);
            });
            sinon.assert.calledOnce(getLengthStub);
            sinon.assert.calledOnce(getByteStub);
            return noop;
        });
        serializer.serialize([testData]);
    });
    it('serializeData', () => {
        getLengthStub.returns(noop);
        serializer.serializeData(testData);
        sinon.assert.calledOnce(getLengthStub);
    });
    it('splitToChunks', () => {
        getByteStub.returns(() => {
            return testInner;
        });
        const result = serializer.splitToChunks(testInner, 2);

        expect(result).to.be.lengthOf(2);
        expect(result[0]).to.be.lengthOf(3);
    });
});
