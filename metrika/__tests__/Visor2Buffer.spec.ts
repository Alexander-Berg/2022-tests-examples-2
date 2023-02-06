import * as chai from 'chai';
import * as sinon from 'sinon';
import * as events from '@src/utils/events';
import * as defer from '@src/utils/defer';
import { taskOf } from '@src/utils/async';
import { Visor2Buffer, MAX_CHUNK_SIZE } from '../Visor2Buffer';
import { AbstractBufferSerializerInterface } from '../serializer/AbstractBufferSerializer';

describe('Visor2Buffer', () => {
    let triggerResult: any[] = [];
    const fakeEmitter: any = {
        trigger: sinon.stub().callsFake(() => triggerResult),
    };
    let setDeferStub: sinon.SinonStub<any, any>;

    const serializeStub = sinon.stub().callsFake((data: any) => taskOf(data));
    const serializeDataStub = sinon
        .stub()
        .callsFake((data: any) => taskOf(data));
    let chunkSize = MAX_CHUNK_SIZE / 3;
    const getRequestBodySizeStub = sinon.stub().callsFake((data: any[]) => {
        return chunkSize * ((Array.isArray(data) && data.length) || 1);
    });
    const splitToChunksStub = sinon
        .stub()
        .callsFake((data: any, chunksNumber: number) => {
            const result: any[] = [];
            for (let i = 0; i < chunksNumber; i += 1) {
                result.push('small chunk');
            }

            return result;
        });

    class FakeSerializer
        implements AbstractBufferSerializerInterface<any, any>
    {
        serialize = serializeStub;

        serializeData = serializeDataStub;

        getRequestBodySize = getRequestBodySizeStub;

        splitToChunks = splitToChunksStub;

        isEnabled = () => true;
    }

    const sandbox = sinon.createSandbox();
    beforeEach(() => {
        sandbox.stub(events, 'emitter').returns(fakeEmitter);
        sandbox.stub(defer, 'clearDefer');
        setDeferStub = sandbox.stub(defer, 'setDefer');
    });

    afterEach(() => {
        triggerResult = [];
        chunkSize = MAX_CHUNK_SIZE / 3;
        serializeStub.resetHistory();
        serializeDataStub.resetHistory();
        getRequestBodySizeStub.resetHistory();
        splitToChunksStub.resetHistory();

        fakeEmitter.trigger.resetHistory();
        sandbox.restore();
    });

    it('Sends data on timeouts ad flushes', () => {
        const ctx: any = {};
        const serializer = new FakeSerializer();
        const senderFunction = sinon.stub().resolves();

        const buffer = new Visor2Buffer(ctx, serializer, senderFunction);
        buffer.push('data' as any);

        sinon.assert.notCalled(senderFunction);

        const [timeoutCtx, callback, timeout] = setDeferStub.getCall(0).args;
        chai.expect(timeoutCtx).to.equal(ctx);
        chai.expect(timeout).to.equal(2000);
        callback();

        let [data] = senderFunction.getCall(0).args;
        chai.expect(data).to.be.deep.eq(['data']);

        triggerResult = ['aggregate'];
        buffer.push('data1' as any);

        buffer.flush();

        [data] = senderFunction.getCall(1).args;
        chai.expect(data).to.be.deep.eq(['data1', 'aggregate']);
    });

    it('Waits for critical mass', () => {
        const ctx: any = {};
        const serializer = new FakeSerializer();
        const senderFunction = sinon.stub().resolves();

        const buffer = new Visor2Buffer(ctx, serializer, senderFunction);
        buffer.push('data1' as any);
        sinon.assert.notCalled(senderFunction);
        buffer.push('data2' as any);
        sinon.assert.notCalled(senderFunction);
        buffer.push('data3' as any);
        const [data] = senderFunction.getCall(0).args;

        chai.expect(data).to.be.deep.eq(['data1', 'data2']);
    });

    it('Splits too big data points to chunks', () => {
        const ctx: any = {};
        const serializer = new FakeSerializer();
        const senderFunction = sinon.stub().resolves();

        const buffer = new Visor2Buffer(ctx, serializer, senderFunction);
        chunkSize = MAX_CHUNK_SIZE + 1;
        buffer.push({ data: 'very big chunk' } as any);
        let [data] = senderFunction.getCall(0).args;
        chai.expect(data).to.be.deep.eq([
            {
                data: 'small chunk',
                partNum: 1,
                end: false,
            },
        ]);

        [data] = senderFunction.getCall(1).args;
        chai.expect(data).to.be.deep.eq([
            {
                data: 'small chunk',
                partNum: 2,
                end: true,
            },
        ]);
    });

    it('stops pushing anything if total size threashold is achieved', () => {
        const ctx: any = {};
        chunkSize = 1;
        const serializer = new FakeSerializer();
        const senderFunction = sinon.stub().resolves();

        const buffer = new Visor2Buffer(ctx, serializer, senderFunction, 1);
        buffer.push('data1' as any);
        buffer.flush();
        const [data] = senderFunction.getCall(0).args;
        chai.expect(data).to.be.deep.eq(['data1']);

        senderFunction.resetHistory();
        buffer.push('data2' as any);
        buffer.flush();
        chai.assert(senderFunction.notCalled);
    });
});
