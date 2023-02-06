import * as sinon from 'sinon';
import { CounterOptions } from '@src/utils/counterOptions';
import { browserInfo } from '@src/utils/browserInfo';
import { REQUEST_MODE_KEY, WATCH_WMODE_JSON } from '@src/transport/watchModes';
import { HIT_PROVIDER } from '@src/providers';
import { WATCH_URL_PARAM } from '@src/sender/watch';
import * as storage from '@src/storage/global';
import { PAGE_VIEW_BR_KEY } from '@src/providers/hit/const';
import { counterFirstHit, IS_EU_CONFIG_KEY } from '../counterFirstHit';

describe('wait for first hit', () => {
    const opt = () => {
        const counterOptions: CounterOptions = {
            id: Math.random() * 100,
            counterType: '0',
        };
        return counterOptions;
    };
    const win = () => {
        return {} as Window;
    };
    const fakeGlobalStorage: any = { setVal: sinon.stub() };

    const sandbox = sinon.createSandbox();
    beforeEach(() => {
        sandbox.stub(storage, 'getGlobalStorage').returns(fakeGlobalStorage);
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('waits for first hit', () => {
        const winInfo = win();
        const brInfo = browserInfo();
        const middleware = counterFirstHit(winInfo, HIT_PROVIDER, opt());
        const next = sinon.stub();

        // not first hit
        middleware.beforeRequest!(
            {
                brInfo,
                urlParams: {
                    [WATCH_URL_PARAM]: 'test-url',
                },
            },
            next,
        );
        sinon.assert.notCalled(next);
        // first hit
        const firstHitParams = {
            brInfo: browserInfo({
                [PAGE_VIEW_BR_KEY]: 1,
            }),
            urlParams: {},
        };
        middleware.beforeRequest!(firstHitParams, next);
        const afterRequestNext = sinon.stub();
        middleware.afterRequest!(firstHitParams, afterRequestNext);

        sinon.assert.calledOnce(afterRequestNext);
        sinon.assert.calledTwice(next);
    });
    it('set isEu flag', () => {
        const winInfo = win();
        const euValue = 0;
        const brInfo = browserInfo({
            [PAGE_VIEW_BR_KEY]: 1,
        });
        const senderParams = {
            brInfo,
            urlParams: {
                [REQUEST_MODE_KEY]: WATCH_WMODE_JSON,
            },
            responseInfo: { settings: { eu: euValue } },
        };
        const middleware = counterFirstHit(winInfo, 'h', opt());

        const next = sandbox.stub();
        middleware.beforeRequest!(senderParams, next);
        sinon.assert.calledOnce(next);
        middleware.afterRequest!(senderParams, next);
        sinon.assert.calledTwice(next);
        sinon.assert.calledWith(
            fakeGlobalStorage.setVal,
            IS_EU_CONFIG_KEY,
            euValue,
        );
    });
});
