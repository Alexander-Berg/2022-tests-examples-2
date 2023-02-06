import chai from 'chai';
import * as sinon from 'sinon';
import * as sender from '@src/sender';
import * as browserInfo from '@src/utils/browserInfo';
import * as defer from '@src/utils/defer';
import * as iters from '@src/utils/async';
import * as pubData from '@private/src/providers/publisher/hasPublisherData';
import { MUTATIONS_BR_KEY, WEBVISOR2_PROVIDER } from '../../const';
import { Visor2SenderBuffer } from '..';

describe('webvisor2 createSenderFunction', () => {
    const ctx: any = {};
    const counterOptions: any = { id: 123 };
    const sandbox = sinon.createSandbox();
    const senderStub = sinon.stub().returns(Promise.resolve());
    const fakeBrowserInfo = {
        setVal: sinon.stub(),
    };
    let setDeferStub: sinon.SinonStub;
    let getSenderStub: sinon.SinonStub;

    beforeEach(() => {
        sandbox
            .stub(iters, 'iterateTaskWithConstraints')
            .callsFake((win, collection, callback, times, errorNS) => {
                chai.expect(win).to.equal(ctx);
                chai.expect(times).to.equal(20);
                chai.expect(errorNS).to.equal('s.w2.sf.fes');
                collection.forEach(callback);
            });
        sandbox.stub(pubData, 'hasPublisherData').returns(false);
        setDeferStub = sandbox.stub(defer, 'setDefer');
        getSenderStub = sandbox
            .stub(sender, 'getSender')
            .returns(senderStub as any);
        sandbox
            .stub(browserInfo, 'browserInfo')
            .returns(fakeBrowserInfo as any);
    });

    afterEach(() => {
        sandbox.restore();
        senderStub.resetHistory();
        fakeBrowserInfo.setVal.resetHistory();
    });

    // потенциально это надо будет вернуть
    it.skip('sends mutations after timeout exceeded', () => {
        const senderBuffer = new Visor2SenderBuffer(
            ctx,
            counterOptions,
            true,
            false,
        );

        const someMutation = { type: 'mutation', data: {} };
        const mutationData = 'mu';

        senderBuffer.mutationsSenderFunction(
            mutationData,
            [someMutation as any],
            1,
        );
        chai.assert(senderStub.notCalled);

        const [deferCtx, callback, timeout] = setDeferStub.getCall(0).args;
        chai.expect(deferCtx).to.eq(ctx);
        chai.expect(timeout).to.equal(5000);
        callback();
        let [senderOpts, counterOpts, partNumber] = senderStub.getCall(0).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: mutationData,
            containsPublisherData: false,
            isBinData: true,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(1);

        const mutationData1 = 'mu1';
        senderBuffer.mutationsSenderFunction(
            mutationData1,
            [someMutation as any],
            2,
        );

        [senderOpts, counterOpts, partNumber] = senderStub.getCall(1).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: mutationData1,
            containsPublisherData: false,
            isBinData: true,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(2);
        chai.assert(senderStub.calledTwice);
    });

    it('Sends events buffer event after page is sent', () => {
        const senderBuffer = new Visor2SenderBuffer(
            ctx,
            counterOptions,
            true,
            false,
        );
        chai.assert(
            getSenderStub.calledWith(ctx, WEBVISOR2_PROVIDER, counterOptions),
        );

        const someEvent = { type: 'event', data: {} } as any;
        const data = '123';
        senderBuffer.eventsSenderFunction(data, [someEvent], 1);
        sinon.assert.notCalled(senderStub);

        const page = { type: 'page', data: {} };
        const pageData = 'pa';
        senderBuffer.mutationsSenderFunction(pageData, [page as any], 2);
        let [senderOpts, counterOpts, partNumber] = senderStub.getCall(0).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: pageData,
            containsPublisherData: false,
            isBinData: true,
        });
        chai.expect(partNumber).to.equal(2);

        [senderOpts, counterOpts, partNumber] = senderStub.getCall(1).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: data,
            containsPublisherData: false,
            isBinData: true,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(1);
    });

    it('flushes mutations after eof is sent', () => {
        const senderBuffer = new Visor2SenderBuffer(
            ctx,
            counterOptions,
            false,
            false,
        );
        chai.assert(
            getSenderStub.calledWith(ctx, WEBVISOR2_PROVIDER, counterOptions),
        );

        const someMutation = { type: 'mutation', data: {} };
        const mutationData = 'mu';
        senderBuffer.mutationsSenderFunction(
            mutationData,
            [someMutation as any],
            1,
        );
        chai.assert(senderStub.notCalled);

        const eof = { type: 'event', data: { type: 'eof' } };
        const eofData = 'eof';

        senderBuffer.mutationsSenderFunction(eofData, [eof as any], 2);
        let [senderOpts, counterOpts, partNumber] = senderStub.getCall(0).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: mutationData,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(1);

        [senderOpts, counterOpts, partNumber] = senderStub.getCall(1).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: eofData,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(2);
        chai.assert(senderStub.calledTwice);
    });

    it('starts to send mutations after page is recieved', () => {
        const senderBuffer = new Visor2SenderBuffer(
            ctx,
            counterOptions,
            false,
            false,
        );
        chai.assert(
            getSenderStub.calledWith(ctx, WEBVISOR2_PROVIDER, counterOptions),
        );

        const someMutation = { type: 'mutation', data: {} };
        const mutationData = 'mu';
        senderBuffer.mutationsSenderFunction(
            mutationData,
            [someMutation as any],
            1,
        );
        chai.assert(senderStub.notCalled);

        const page = { type: 'page', data: {} };
        const pageData = 'pa';
        senderBuffer.mutationsSenderFunction(pageData, [page as any], 2);

        let [senderOpts, counterOpts, partNumber] = senderStub.getCall(0).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: pageData,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(2);

        [senderOpts, counterOpts, partNumber] = senderStub.getCall(1).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: mutationData,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(1);

        chai.assert(fakeBrowserInfo.setVal.calledWith(MUTATIONS_BR_KEY, 1));
        chai.assert(fakeBrowserInfo.setVal.calledTwice);
        chai.assert(senderStub.calledTwice);
    });

    it('awaits all the page chunks before sending', () => {
        const senderBuffer = new Visor2SenderBuffer(
            ctx,
            counterOptions,
            false,
            false,
        );
        chai.assert(
            getSenderStub.calledWith(ctx, WEBVISOR2_PROVIDER, counterOptions),
        );

        const someMutation = { type: 'mutation', data: {} };
        const mutationData = 'mu';
        senderBuffer.mutationsSenderFunction(
            mutationData,
            [someMutation as any],
            1,
        );
        chai.assert(senderStub.notCalled);

        const pageChunk1 = { type: 'page', partNum: 1, end: false, data: {} };
        const pageChunkData1 = 'p1';
        senderBuffer.mutationsSenderFunction(
            pageChunkData1,
            [pageChunk1 as any],
            2,
        );
        chai.assert(senderStub.notCalled);

        const pageChunk2 = { type: 'page', partNum: 2, end: false, data: {} };
        const pageChunkData2 = 'p2';
        senderBuffer.mutationsSenderFunction(
            pageChunkData2,
            [pageChunk2 as any],
            3,
        );
        chai.assert(senderStub.notCalled);

        const pageChunk3 = { type: 'page', partNum: 3, end: true, data: {} };
        const pageChunkData3 = 'p3';
        senderBuffer.mutationsSenderFunction(
            pageChunkData3,
            [pageChunk3 as any],
            4,
        );
        let [senderOpts, counterOpts, partNumber] = senderStub.getCall(0).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: pageChunkData1,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(2);

        [senderOpts, counterOpts, partNumber] = senderStub.getCall(1).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: pageChunkData2,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(3);

        [senderOpts, counterOpts, partNumber] = senderStub.getCall(2).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: pageChunkData3,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(4);

        [senderOpts, counterOpts, partNumber] = senderStub.getCall(3).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: mutationData,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(1);

        chai.assert(fakeBrowserInfo.setVal.calledWith(MUTATIONS_BR_KEY, 1));

        senderBuffer.mutationsSenderFunction(
            mutationData,
            [someMutation as any],
            5,
        );
        [senderOpts, counterOpts, partNumber] = senderStub.getCall(4).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: mutationData,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(5);
        chai.expect(senderStub.getCalls().length).to.equal(5);
    });

    it('correctly handles small pages mixed with mutations', () => {
        const senderBuffer = new Visor2SenderBuffer(
            ctx,
            counterOptions,
            false,
            false,
        );
        chai.assert(
            getSenderStub.calledWith(ctx, WEBVISOR2_PROVIDER, counterOptions),
        );

        const someMutation = { type: 'mutation', data: {} };
        const mutationData = 'mu';
        senderBuffer.mutationsSenderFunction(
            mutationData,
            [someMutation as any],
            1,
        );
        chai.assert(senderStub.notCalled);

        const page = { type: 'page', data: {} };
        const pageAndMutationsData = 'page and some mutations';
        senderBuffer.mutationsSenderFunction(
            pageAndMutationsData,
            [someMutation as any, page as any, someMutation as any],
            2,
        );

        chai.assert(senderStub.calledTwice);
        let [senderOpts, counterOpts, partNumber] = senderStub.getCall(0).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: pageAndMutationsData,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(2);

        [senderOpts, counterOpts, partNumber] = senderStub.getCall(1).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: mutationData,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(1);

        senderBuffer.mutationsSenderFunction(
            mutationData,
            [someMutation as any],
            3,
        );

        [senderOpts, counterOpts, partNumber] = senderStub.getCall(2).args;
        chai.expect(senderOpts).to.deep.equal({
            urlParams: {},
            brInfo: fakeBrowserInfo,
            rBody: mutationData,
            containsPublisherData: false,
            isBinData: false,
        });
        chai.expect(counterOptions).to.equal(counterOpts);
        chai.expect(partNumber).to.equal(3);
        chai.expect(senderStub.calledThrice);
    });
});
