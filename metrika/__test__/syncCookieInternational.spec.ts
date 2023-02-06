import Sinon, * as sinon from 'sinon';
import * as ls from '@src/storage/localStorage';
import * as gs from '@src/storage/global';
import * as counterSettings from '@src/utils/counterSettings';
import * as defaultSender from '@src/sender/default';
import * as time from '@src/utils/time';
import * as transports from '@src/transport';
import {
    COOKIE_SYNC_INTERNATIONAL_PROVIDER,
    COOKIE_SYNC_PROVIDER,
} from '@src/providers';
import * as uid from '@src/utils/uid';
import * as hid from '@src/middleware/watchSyncFlags/brinfoFlags/hid';
import { CounterOptions } from '@src/utils/counterOptions';
import { CounterSettings } from '@src/utils/counterSettings';
import { TransportOptions } from '@src/transport/types';
import { DefaultSenderResult } from '@src/sender/default';
import { InternalSenderInfo } from '@src/sender/SenderInfo';
import * as constInfo from '../const';
import { syncCookieInternationalRaw } from '../syncCookieInternational';

const { COUNTER_SYNC_URL, DUID_URL_PARAM_KEY, SYNC_REQUEST_TIMEOUT } =
    constInfo;

describe('syncCookieInternational', () => {
    const sandbox = sinon.createSandbox();
    const now = 100;
    const uidValue = '123';
    const hidValue = 11;
    const fakeLS: any = {
        state: {},
        getVal: <T>(key: string, defaultValue?: T) => {
            return fakeLS.state[key] || defaultValue;
        },
        setVal: sinon.stub(),
    };
    const fakeGS: any = {
        state: {},
        getVal: <T>(key: string, defaultValue?: T) => {
            return fakeGS.state[key] || defaultValue;
        },
        setVal: sinon.stub(),
    };
    let getTransportList: Sinon.SinonStub;
    let getDefaultSender: Sinon.SinonStub;

    const responseData: Record<string, any> = {};
    const defaultSenderStub: Sinon.SinonStub<
        [
            senderInfo: InternalSenderInfo,
            urls: string[],
            opt?: TransportOptions,
        ],
        Promise<DefaultSenderResult>
    > = sinon.stub();

    const ctx = {} as Window;
    const counterOpts = {
        id: 1,
        counterType: 0,
    } as unknown as CounterOptions;
    const settings = {
        settings: {
            ins: 1,
        },
    } as unknown as CounterSettings;
    const resultingTransport = {} as transports.TransportList;

    beforeEach(() => {
        fakeLS.state = {};
        fakeGS.state = {};
        sandbox.stub(time, 'TimeOne').returns(() => now as any);
        sandbox
            .stub(counterSettings, 'getCounterSettings')
            .callsFake(() => Promise.resolve(settings));
        sandbox.stub(ls, 'localStorage').returns(fakeLS);
        sandbox.stub(gs, 'getGlobalStorage').returns(fakeGS);
        fakeGS.setVal.callsFake(<T>(key: string, value: T) => {
            fakeGS.state[key] = value;
            return fakeGS;
        });
        getTransportList = sandbox
            .stub(transports, 'getTransportList')
            .returns(resultingTransport);
        getDefaultSender = sandbox
            .stub(defaultSender, 'useDefaultSender')
            .returns(defaultSenderStub);
        sandbox.stub(uid, 'getUid').returns(uidValue);
        sandbox.stub(hid, 'getHid').returns(hidValue);
        defaultSenderStub.resolves({ responseData, urlIndex: 0 });
    });

    afterEach(() => {
        sandbox.restore();
        fakeGS.setVal.resetHistory();
        fakeLS.setVal.resetHistory();
        defaultSenderStub.resetHistory();
        settings.settings.ins = 1;
    });

    it('does nothing if settings.ins = 0', async () => {
        settings.settings.ins = 0;
        await syncCookieInternationalRaw(ctx, counterOpts)!;
        sinon.assert.notCalled(getDefaultSender);
        sinon.assert.notCalled(fakeGS.setVal);
    });

    it('does nothing if sync is in progress', async () => {
        fakeGS.state[constInfo.COUNTER_SYNC_PROGRESS_KEY] = '0';
        await syncCookieInternationalRaw(ctx, counterOpts);
        sinon.assert.notCalled(getDefaultSender);
        sinon.assert.notCalled(fakeGS.setVal);
    });

    it('does nothing if sync not expired', async () => {
        fakeLS.state = {
            [constInfo.COUNTER_SYNC_TIME_LS_KEY]: `${now}`, // sync not expired
        };

        await syncCookieInternationalRaw(ctx, counterOpts);

        sinon.assert.calledWith(
            getTransportList,
            ctx,
            COOKIE_SYNC_INTERNATIONAL_PROVIDER,
        );
        sinon.assert.calledWith(getDefaultSender, ctx, resultingTransport);
        sinon.assert.notCalled(defaultSenderStub);
        sinon.assert.notCalled(fakeGS.setVal);
    });

    it('requests sync urls and does nothing if the list is not provided', async () => {
        await syncCookieInternationalRaw(ctx, counterOpts);

        sinon.assert.calledTwice(getTransportList);
        sinon.assert.calledWith(
            getTransportList.getCall(0),
            ctx,
            COOKIE_SYNC_INTERNATIONAL_PROVIDER,
        );
        sinon.assert.calledWith(
            getTransportList.getCall(1),
            ctx,
            COOKIE_SYNC_PROVIDER,
        );
        sinon.assert.calledTwice(getDefaultSender);
        getDefaultSender
            .getCalls()
            .forEach((call) =>
                sinon.assert.calledWith(call, ctx, resultingTransport),
            );
        sinon.assert.calledOnce(defaultSenderStub);
        sinon.assert.notCalled(fakeLS.setVal);
    });

    it('syncs cookies if not synced already', async () => {
        fakeLS.state = {};
        fakeGS.state = {};
        responseData.CookieMatchUrls = [
            'an.yandex.ru/mapuid/google/?partner-tag=yandex_ag&enable_guid_cm_redir=1&google_ula=123',
            'an.yandex.ru/mapuid/betweenx/',
            'an.yandex.ru/mapuid/operacom/',
        ];

        await syncCookieInternationalRaw(ctx, counterOpts);

        sinon.assert.calledTwice(getTransportList);
        sinon.assert.calledWith(
            getTransportList.getCall(0),
            ctx,
            COOKIE_SYNC_INTERNATIONAL_PROVIDER,
        );
        sinon.assert.calledWith(
            getTransportList.getCall(1),
            ctx,
            COOKIE_SYNC_PROVIDER,
        );
        sinon.assert.calledTwice(getDefaultSender);
        getDefaultSender
            .getCalls()
            .forEach((call) =>
                sinon.assert.calledWith(call, ctx, resultingTransport),
            );
        sinon.assert.callCount(defaultSenderStub, 4);
        [COUNTER_SYNC_URL, ...responseData.CookieMatchUrls].forEach(
            (url, index) => {
                const transportOptions: TransportOptions = {
                    timeOut: SYNC_REQUEST_TIMEOUT,
                };
                if (index === 0) {
                    transportOptions.wmode = true;
                }
                const fullUrl =
                    index === 0
                        ? url
                        : `${url}${
                              url.includes('?') ? '&' : '?'
                          }${DUID_URL_PARAM_KEY}=${uidValue}`;
                sinon.assert.calledWith(
                    defaultSenderStub.getCall(index),
                    sinon.match.any,
                    [`https://${fullUrl}`],
                    transportOptions,
                );
            },
        );
        sinon.assert.calledOnceWithExactly(
            fakeLS.setVal,
            `${constInfo.COUNTER_SYNC_TIME_LS_KEY}`,
            now,
        );
        sinon.assert.calledThrice(fakeGS.setVal);
        ['0', '01', '012'].forEach((progress, index) => {
            sinon.assert.calledWith(
                fakeGS.setVal.getCall(index),
                constInfo.COUNTER_SYNC_PROGRESS_KEY,
                progress,
            );
        });
    });
});
