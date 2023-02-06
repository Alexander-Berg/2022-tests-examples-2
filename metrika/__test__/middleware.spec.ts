import * as sinon from 'sinon';
import { useMiddlewareSender } from '@src/sender/middleware';
import * as middleware from '@src/middleware/combine';
import * as indexer from '@src/providers/hostIndexer';
import * as defaultSender from '@src/sender/default';
import { noop } from '@src/utils/function';
import { expect } from 'chai';
import { InternalSenderInfo } from '@src/sender/SenderInfo';

describe('sender/middleware', () => {
    let defaultSenderFake: any;
    let useDefaultSenderStub: sinon.SinonStub<any, any>;
    let combineMiddlewaresStub: sinon.SinonStub<any, any>;
    let fullhostStub: sinon.SinonStub<any, any>;
    let hostIndexerStub: sinon.SinonStub<any, any>;
    const sandbox = sinon.createSandbox();

    const testData = 'testDate';

    beforeEach(() => {
        defaultSenderFake = sandbox.stub().resolves({
            responseData: testData,
            urlIndex: 1,
        });
        fullhostStub = sandbox.stub(indexer, 'returnFullHost');
        fullhostStub.returns([]);
        hostIndexerStub = sandbox.stub(indexer, 'getHostIndexer');
        hostIndexerStub.returns(noop);
        combineMiddlewaresStub = sandbox.stub(middleware, 'combineMiddlewares');
        useDefaultSenderStub = sandbox.stub(defaultSender, 'useDefaultSender');
        useDefaultSenderStub.returns(defaultSenderFake);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Middlewares resolve', () => {
        combineMiddlewaresStub.resolves({});
        const senderInfo: InternalSenderInfo = { debugStack: [1] };
        const sender = useMiddlewareSender({} as any, [], []);
        return sender(senderInfo, '').then((result) => {
            expect(result).to.be.eq(testData);
            expect(senderInfo.responseInfo).to.be.eq(testData);
            sinon.assert.calledOnce(defaultSenderFake);
            sinon.assert.calledTwice(combineMiddlewaresStub);
        });
    });

    it('Middlewares reject', () => {
        combineMiddlewaresStub.rejects();

        const sender = useMiddlewareSender({} as any, [], []);
        return sender({ debugStack: [] }, '').catch(() => {
            sinon.assert.notCalled(defaultSenderFake);
            sinon.assert.calledOnce(combineMiddlewaresStub);
        });
    });
});
