import * as sinon from 'sinon';
import { adBlock } from '@src/providers/adBlock';
import {
    AD_BLOCK_COOKIE,
    AD_BLOCK_ENABLED,
    AD_BLOCK_DISABLED,
    AD_BLOCK_COOKIE_TTL,
} from '@src/providers/adBlock/const';
import * as br from '@src/utils/browser';
import * as sender from '@src/sender';
import * as cookieStorage from '@src/storage/cookie';
import * as globalStorage from '@src/storage/global';
import * as events from '@src/utils/events/ready';
import { CounterOptions } from '@src/utils/counterOptions';

describe('adBlock.ts', () => {
    const windowStub = {} as any;
    const sandbox = sinon.createSandbox();
    const counterOptions = () =>
        ({
            id: 10,
            counterType: '0',
        } as CounterOptions);
    const setCookieStub = sandbox.stub();
    const cookieStore = {
        getVal: () => null,
        setVal: setCookieStub,
    };
    const globalStore = {
        getVal: () => null,
        setVal: sandbox.stub(),
    };
    let cookieStub: sinon.SinonStub<any, any>;
    let globalStub: sinon.SinonStub<any, any>;
    let eventsStub: sinon.SinonStub<any, any>;
    let getSenderStub: sinon.SinonStub<any, any>;
    let fromCharCodeStub: sinon.SinonStub<any, any>;

    const senderStub = sandbox.stub();

    beforeEach(() => {
        fromCharCodeStub = sandbox.stub(br, 'isBrokenFromCharCode');
        fromCharCodeStub.returns(false);
        cookieStub = sandbox.stub(cookieStorage, 'globalCookieStorage');
        cookieStub.returns(cookieStore as any);

        globalStub = sandbox.stub(globalStorage, 'getGlobalStorage');
        globalStub.returns(globalStore as any);

        eventsStub = sandbox.stub(events, 'runCallbackOnReady');
        senderStub.returns(Promise.resolve());
        getSenderStub = sandbox.stub(sender, 'getSender');
        getSenderStub.returns(senderStub);
    });

    afterEach(() => {
        sandbox.resetHistory();
        sandbox.restore();
    });

    it('not set cookie if it disabled', () => {
        const opt = counterOptions();
        opt.noCookie = true;
        adBlock(windowStub, opt);
        sinon.assert.notCalled(cookieStub);
    });

    it('set ad block disabled', (done) => {
        eventsStub.callsFake((ctx: any, cb: any) => {
            cb().then(() => {
                sinon.assert.calledWith(
                    setCookieStub,
                    AD_BLOCK_COOKIE,
                    AD_BLOCK_DISABLED,
                    AD_BLOCK_COOKIE_TTL,
                );
                done();
            });
        });

        adBlock(windowStub, counterOptions());
    });

    it('set ad block enabled', (done) => {
        senderStub.returns(Promise.reject());
        eventsStub.callsFake((ctx: any, cb: any) => {
            cb().then(() => {
                sinon.assert.calledWith(
                    setCookieStub,
                    AD_BLOCK_COOKIE,
                    AD_BLOCK_ENABLED,
                    AD_BLOCK_COOKIE_TTL,
                );
                done();
            });
        });

        adBlock(windowStub, counterOptions());
    });
});
