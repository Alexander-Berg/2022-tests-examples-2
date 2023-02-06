import * as chai from 'chai';
import * as sinon from 'sinon';
import * as errorLogger from '@src/utils/errorLogger';
import * as sender from '@src/sender/index';
import * as browserInfo from '@src/utils/browserInfo';
import * as DebugConsole from '@src/providers/debugConsole';
import { WATCH_URL_PARAM, WATCH_REFERER_PARAM } from '@src/sender/watch';
import { PAGE_VIEW_BR_KEY } from '@src/providers/hit/const';
import { syncPromise } from '@src/__tests__/utils/syncPromise';
import { artificialHitProvider } from '../artificialHit';
import { ARTIFICIAL_BR_KEY } from '../type';

describe('providers / artificial hit', () => {
    const sandbox = sinon.createSandbox();
    const senderStub = sandbox.stub().returns(syncPromise);
    let logSpy: sinon.SinonSpy;
    let getSenderStub: sinon.SinonStub<any, any>;
    let errorLoggerStub: sinon.SinonStub<any, any>;
    let debugConsoleStub: sinon.SinonStub<any, any>;
    let browserInfoStub: sinon.SinonStub<any, any>;

    beforeEach(() => {
        browserInfoStub = sandbox.stub(browserInfo, 'browserInfo');
        browserInfoStub.callsFake((obj) => obj as any);
        logSpy = sandbox.spy();
        debugConsoleStub = sandbox.stub(DebugConsole, 'getLoggerFn');
        debugConsoleStub.returns(logSpy as any);
        getSenderStub = sandbox.stub(sender, 'getSender');
        getSenderStub.returns(senderStub);

        errorLoggerStub = sandbox.stub(errorLogger, 'errorLogger');

        errorLoggerStub.callsFake((ctx, scopeName, fn) => {
            return (...args: any[]) => {
                if (fn) {
                    fn(...args);
                }
            };
        });
    });

    afterEach(() => {
        senderStub.resetHistory();
        sandbox.restore();
    });

    it('sends artificial hit and ignores artificial hit if url is not changed', () => {
        const counterOptions: any = { id: 123 };
        const ctx = {};
        const params = {
            a: 1,
            b: 1,
        };
        const callback = sinon.stub();
        const context = {};
        const referer = 'reff';
        const title = 'Title';
        const url = 'http://example.com';

        const makeArtificialHit = artificialHitProvider(
            ctx as any,
            counterOptions,
        );
        makeArtificialHit(url, title, referer, params, callback, context);
        sinon.assert.calledOnce(logSpy);
        const [senderOptions, counterOptionsCalled] =
            senderStub.getCall(0).args;
        chai.expect(counterOptionsCalled).to.equal(counterOptions);
        chai.expect(senderOptions).to.deep.equal({
            params,
            urlParams: {
                [WATCH_URL_PARAM]: url,
                [WATCH_REFERER_PARAM]: referer,
            },
            brInfo: {
                [PAGE_VIEW_BR_KEY]: 1,
                [ARTIFICIAL_BR_KEY]: 1,
            },
            title,
        });
        sinon.assert.calledOnce(callback);
        chai.expect(callback.thisValues[0]).to.be.equal(context);
    });
});
