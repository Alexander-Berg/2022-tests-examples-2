import * as chai from 'chai';
import * as sinon from 'sinon';
import { browserInfo } from '@src/utils/browserInfo';
import { config } from '@src/config';
import { DEFER_KEY } from '@src/sender/SenderInfo';
import * as browser from '@src/utils/browser';
import * as timeFlags from '@src/middleware/watchSyncFlags/brinfoFlags/timeFlags';
import * as decoder from '@src/utils/decoder';
import * as timeUtils from '@src/utils/time';
import * as globalStorage from '@src/storage/global';
import * as random from '@src/utils/number';
import * as localStorageStorage from '@src/storage/localStorage';
import { setTurboInfo } from '@src/utils/counterOptions';
import { REQUEST_NUMBER_KEY, LS_ID_KEY } from '../consts';
import { IS_ACTIVE_WINDOW_TEL_KEY } from '../telemetryFlags/keys';
import {
    HID_BR_KEY,
    BUILD_VERSION_BR_KEY,
    LS_ID_BR_KEY,
    COUNTER_NUMBER_BR_KEY,
    COOKIES_ENABLED_BR_KEY,
    DEVICE_PIXEL_RATIO_BR_KEY,
    RANDOM_NUMBER_BR_KEY,
    REQUEST_NUMBER_BR_KEY,
    IS_TURBO_PAGE_BR_KEY,
    IS_IFRAME_BR_KEY,
    TURBO_PAGE_ID_BR_KEY,
    IS_JAVA_ENABLED,
    IS_SAME_ORIGIN_AS_TOP_WINDOW,
    VIEWPORT_SIZE_BR_KEY,
    SCREEN_SIZE_BR_KEY,
    NOINDEX_BR_KEY,
    NOTIFICATION_PERMISSION,
    WEBVISOR2_ENABLED_BR_KEY,
    NAVIGATOR_PLATFORM,
    IS_TURBO_APP_BR_KEY,
} from '../brinfoFlags/keys';
import { TELEMETRY_FLAG_GETTERS } from '../telemetryFlags';
import { BRINFO_FLAG_GETTERS, COUNTER_NO } from '../brinfoFlags';
import { watchSyncFlags } from '..';
import { HID_NAME } from '../brinfoFlags/hid';

describe('watchSyncFlags', () => {
    const testHid = 'testHid';
    const testLsID = 11111;
    const randomNumber = 1488;
    const testTpid = 123;
    const counterOpt: any = {
        id: 1,
        counterType: '0',
    };
    const nowMs = 100;
    const senderParams: any = {};
    const sandbox = sinon.createSandbox();
    let globalStorageStub: sinon.SinonStub<any, any>;
    let getRandomStub: sinon.SinonStub<any, any>;
    const lsGetValStub = sandbox.stub();
    const lsSetValStub = sandbox.stub();
    const lsDelValStub = sandbox.stub();
    const globalGetValStub = sandbox.stub();
    const globalSetValStub = sandbox.stub();
    let timeZoneStub: sinon.SinonStub<any, any>;
    let timeOneStub: sinon.SinonStub<any, any>;
    let globalLocalStorageStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        globalStorageStub = sandbox.stub(globalStorage, 'getGlobalStorage');
        globalStorageStub.returns({
            getVal: globalGetValStub,
            setVal: globalSetValStub,
        });
        getRandomStub = sandbox.stub(random, 'getRandom');
        getRandomStub.returns(randomNumber);
        timeOneStub = sandbox.stub(timeUtils, 'TimeOne');
        timeOneStub.returns(() => nowMs);
        timeZoneStub = sandbox.stub(timeFlags, 'timeZone');
        timeZoneStub.returns(nowMs);
        globalLocalStorageStub = sandbox.stub(
            localStorageStorage,
            'counterLocalStorage',
        );
        globalLocalStorageStub.returns({
            getVal: lsGetValStub,
            setVal: lsSetValStub,
            delVal: lsDelValStub,
        });
    });

    afterEach(() => {
        sandbox.restore();
    });

    it(`sets ${HID_BR_KEY}`, () => {
        const winInfo = {} as any;
        const fn = BRINFO_FLAG_GETTERS[HID_BR_KEY];
        globalGetValStub.returns(testHid);
        const result = fn(winInfo, counterOpt, {});
        chai.expect(result).to.be.equal(testHid);
        sinon.assert.calledWith(globalGetValStub, HID_NAME);
        globalGetValStub.returns(null);
        const secondResult = fn(winInfo, counterOpt, senderParams);
        chai.expect(secondResult).to.be.equal(randomNumber);
        sinon.assert.calledWith(globalSetValStub, HID_NAME, randomNumber);
    });

    it(`sets ${WEBVISOR2_ENABLED_BR_KEY}`, () => {
        const win = {} as any;
        const options = { webvisor: true } as any;
        chai.expect(
            BRINFO_FLAG_GETTERS[WEBVISOR2_ENABLED_BR_KEY](win, options, {}),
        ).to.equal(1);
        options.webvisor = false;
        chai.expect(
            BRINFO_FLAG_GETTERS[WEBVISOR2_ENABLED_BR_KEY](win, options, {}),
        ).to.equal(null);
    });

    it(`sets ${COUNTER_NUMBER_BR_KEY}`, () => {
        const winInfo = {} as any;
        const no = 10;
        const expectNo = no + 1;
        globalGetValStub.returns(no);
        const fn = BRINFO_FLAG_GETTERS[COUNTER_NUMBER_BR_KEY];
        const result = fn(winInfo, counterOpt, senderParams);
        chai.expect(result).to.be.equal(expectNo);
        sinon.assert.calledWith(globalSetValStub, COUNTER_NO, expectNo);
    });

    it(`sets ${LS_ID_BR_KEY}`, () => {
        const newCounterOpt = () => Object.assign({}, counterOpt);
        const fn = BRINFO_FLAG_GETTERS[LS_ID_BR_KEY];
        const win = {
            Math,
        } as Window;
        // 1. Кейс когда запись в ls уже есть
        lsGetValStub.returns(testLsID);
        const result = fn(win, newCounterOpt(), senderParams);
        sinon.assert.calledWith(globalLocalStorageStub, win, counterOpt.id);
        sinon.assert.calledWith(lsGetValStub, LS_ID_KEY);
        chai.expect(result).to.be.equal(testLsID);
        sinon.assert.notCalled(lsSetValStub);

        // 2. кейс, когда записи нет
        lsGetValStub.returns(null);
        const expectNo = 666;
        getRandomStub.returns(expectNo);
        const secondResult = fn(win, newCounterOpt(), senderParams);
        chai.expect(secondResult).to.be.equal(expectNo);
        sinon.assert.calledWith(lsSetValStub, LS_ID_KEY, expectNo);
    });

    it(`sets ${BUILD_VERSION_BR_KEY}`, () => {
        const winInfo = {} as any;
        chai.expect(
            BRINFO_FLAG_GETTERS[BUILD_VERSION_BR_KEY](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(config.buildVersion);
    });

    it(`sets ${COOKIES_ENABLED_BR_KEY}`, () => {
        const winInfo = {
            navigator: {
                cookieEnabled: true,
            },
        } as any;
        chai.expect(
            BRINFO_FLAG_GETTERS[COOKIES_ENABLED_BR_KEY](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(1);
    });

    it(`sets ${IS_ACTIVE_WINDOW_TEL_KEY}`, () => {
        const window: any = {
            Math,
            document: {},
        };
        chai.expect(
            TELEMETRY_FLAG_GETTERS[IS_ACTIVE_WINDOW_TEL_KEY](
                window,
                counterOpt,
                senderParams,
            ),
        ).to.equal(null);

        window.document.hidden = true;
        chai.expect(
            TELEMETRY_FLAG_GETTERS[IS_ACTIVE_WINDOW_TEL_KEY](
                window,
                counterOpt,
                senderParams,
            ),
        ).to.equal(0);

        window.document.hidden = false;
        chai.expect(
            TELEMETRY_FLAG_GETTERS[IS_ACTIVE_WINDOW_TEL_KEY](
                window,
                counterOpt,
                senderParams,
            ),
        ).to.equal(1);
    });

    // не получится в лоб использовать stub
    // так как функция определяется при импорте
    // и переписать ее не получится
    it(`sets ${RANDOM_NUMBER_BR_KEY}`, () => {
        const winInfo: any = {
            Math,
        };
        const result = BRINFO_FLAG_GETTERS[RANDOM_NUMBER_BR_KEY](
            winInfo,
            counterOpt,
            senderParams,
        );
        chai.expect(typeof result).to.be.equal('number');
    });

    it(`sets ${REQUEST_NUMBER_BR_KEY}`, () => {
        const win = {} as any;
        const fn = BRINFO_FLAG_GETTERS[REQUEST_NUMBER_BR_KEY];
        let newVal = 0;
        lsSetValStub.callsFake((key, val) => {
            chai.expect(key).to.be.eq(REQUEST_NUMBER_KEY);
            newVal = val;
        });
        lsGetValStub.callsFake((key) => {
            chai.expect(key).to.be.eq(REQUEST_NUMBER_KEY);
            return newVal;
        });
        const result = fn(win, counterOpt, {
            urlParams: {},
        });
        chai.expect(result).to.be.equal(1);
        const secondResult = fn(win, counterOpt, {
            urlParams: { [DEFER_KEY]: '1' },
        });
        chai.expect(secondResult).to.be.equal(null);

        newVal = 1;
        const thirdResult = fn(win, counterOpt, {
            urlParams: {},
        });
        chai.expect(thirdResult).to.be.equal(2);

        lsGetValStub.returns(null);
        sinon.assert.notCalled(lsDelValStub);
        const fourthResult = fn(win, counterOpt, {
            urlParams: {},
        });
        chai.expect(fourthResult).to.be.equal(null);
        sinon.assert.calledWith(lsDelValStub, REQUEST_NUMBER_KEY);
    });

    it(`sets ${IS_TURBO_PAGE_BR_KEY}`, () => {
        const winInfo: any = {};
        const counterOptions: any = {
            ...counterOpt,
            id: 100,
        };
        chai.expect(
            BRINFO_FLAG_GETTERS[IS_TURBO_PAGE_BR_KEY](
                winInfo,
                counterOptions,
                senderParams,
            ),
        ).to.be.equal(null);

        setTurboInfo(counterOptions, {
            // eslint-disable-next-line camelcase
            __ym: { turbo_page: 1, turbo_page_id: testTpid },
        });
        chai.expect(
            BRINFO_FLAG_GETTERS[IS_TURBO_PAGE_BR_KEY](
                winInfo,
                counterOptions,
                senderParams,
            ),
        ).to.be.equal(1);
    });

    it(`sets ${TURBO_PAGE_ID_BR_KEY}`, () => {
        const winInfo: any = {};
        const counterOptions: any = {
            ...counterOpt,
            id: 101,
        };
        chai.expect(
            BRINFO_FLAG_GETTERS[TURBO_PAGE_ID_BR_KEY](
                winInfo,
                counterOptions,
                senderParams,
            ),
        ).to.be.equal(null);

        setTurboInfo(counterOptions, {
            // eslint-disable-next-line camelcase
            __ym: { turbo_page: 1, turbo_page_id: testTpid },
        });
        chai.expect(
            BRINFO_FLAG_GETTERS[TURBO_PAGE_ID_BR_KEY](
                winInfo,
                counterOptions,
                senderParams,
            ),
        ).to.be.equal(testTpid);
    });

    it(`sets ${VIEWPORT_SIZE_BR_KEY}`, () => {
        const winInfo = {
            document: {
                compatMode: 'CSS1Compat',
                getElementsByTagName: (name: string) => {
                    if (name === 'body') {
                        return [{}];
                    }

                    return null;
                },
                documentElement: {
                    clientHeight: 100,
                    clientWidth: 200,
                },
            },
        } as any;
        chai.expect(
            BRINFO_FLAG_GETTERS[VIEWPORT_SIZE_BR_KEY](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal('200x100');
    });

    it(`sets ${SCREEN_SIZE_BR_KEY}`, () => {
        const winInfo = {
            screen: {
                width: 100,
                height: 200,
                colorDepth: 10,
            },
        } as any;
        chai.expect(
            BRINFO_FLAG_GETTERS[SCREEN_SIZE_BR_KEY](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal('100x200x10');
    });

    it(`sets ${DEVICE_PIXEL_RATIO_BR_KEY}`, () => {
        const winInfo: any = {
            devicePixelRatio: 3,
        };
        chai.expect(
            BRINFO_FLAG_GETTERS[DEVICE_PIXEL_RATIO_BR_KEY](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(3);
    });
    it(`sets ${NOINDEX_BR_KEY}`, () => {
        const winInfo: any = {
            location: {
                hostname: 'yandex.ru',
            },
        };
        const urlParams: Record<string, any> = {};
        winInfo.top = winInfo;
        BRINFO_FLAG_GETTERS[NOINDEX_BR_KEY](winInfo, counterOpt, {
            urlParams,
        });
        chai.expect(urlParams[NOINDEX_BR_KEY]).to.be.equal('noindex');
    });
    it(`sets ${IS_IFRAME_BR_KEY}`, () => {
        let winInfo: any = {};
        winInfo.top = winInfo;
        chai.expect(
            BRINFO_FLAG_GETTERS[IS_IFRAME_BR_KEY](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(null);

        winInfo = { top: {} };
        chai.expect(
            BRINFO_FLAG_GETTERS[IS_IFRAME_BR_KEY](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(1);
    });

    it(`sets ${IS_JAVA_ENABLED}`, () => {
        let winInfo = { navigator: { javaEnabled: () => true } } as any;
        chai.expect(
            BRINFO_FLAG_GETTERS[IS_JAVA_ENABLED](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(1);

        winInfo = { navigator: { javaEnabled: () => false } } as any;
        chai.expect(
            BRINFO_FLAG_GETTERS[IS_JAVA_ENABLED](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(null);
    });

    it(`sets ${IS_SAME_ORIGIN_AS_TOP_WINDOW}`, () => {
        let winInfo = { top: { contentWindow: {} } } as any;
        chai.expect(
            BRINFO_FLAG_GETTERS[IS_SAME_ORIGIN_AS_TOP_WINDOW](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal('1');

        winInfo = {};
        chai.expect(
            BRINFO_FLAG_GETTERS[IS_SAME_ORIGIN_AS_TOP_WINDOW](
                winInfo,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(null);
    });

    it('sets determined flags', () => {
        const flags = [COUNTER_NUMBER_BR_KEY, BUILD_VERSION_BR_KEY];
        globalGetValStub.withArgs(COUNTER_NO).returns(1);

        const ctx = {} as any;
        const brInfo = browserInfo();
        const newCounterOpt: any = {
            id: counterOpt.id + 1,
            counterType: '0',
        };
        const nextFn = sinon.spy();
        const mv = watchSyncFlags(flags)(ctx, 'p', newCounterOpt);
        mv.beforeRequest!({ brInfo, urlParams: {} }, nextFn);
        sinon.assert.calledOnce(nextFn);
        const flagVal = flags.map((flag) => {
            return brInfo.getVal(flag);
        });
        chai.expect(flagVal).to.include.all.members([2, config.buildVersion]);
    });

    it(`sets ${NOTIFICATION_PERMISSION}`, () => {
        let value: any = true;
        const isNotificationAllowedStub = sinon
            .stub(browser, 'isNotificationAllowed')
            .callsFake(() => value);
        chai.expect(
            BRINFO_FLAG_GETTERS[NOTIFICATION_PERMISSION](
                {} as any,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(2);

        value = false;
        chai.expect(
            BRINFO_FLAG_GETTERS[NOTIFICATION_PERMISSION](
                {} as any,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(1);

        value = null;
        chai.expect(
            BRINFO_FLAG_GETTERS[NOTIFICATION_PERMISSION](
                {} as any,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(null);

        isNotificationAllowedStub.restore();
    });

    it(`sets ${NAVIGATOR_PLATFORM}`, () => {
        const platform = 'MacIntel';
        const winCtx = { navigator: { platform } } as any;

        const encodeUtf8Stub = sinon
            .stub(decoder, 'encodeUtf8')
            .callsFake((value) => value as any);
        const encodeBase64Stub = sinon
            .stub(decoder, 'encodeBase64')
            .callsFake((value) => value as any);

        getRandomStub.returns(0);
        chai.expect(
            BRINFO_FLAG_GETTERS[NAVIGATOR_PLATFORM](
                winCtx,
                counterOpt,
                senderParams,
            ),
        ).to.be.equal(platform);

        getRandomStub.returns(1);
        chai.expect(
            BRINFO_FLAG_GETTERS[NAVIGATOR_PLATFORM](
                winCtx,
                counterOpt,
                senderParams,
            ),
        ).to.be.null;

        encodeUtf8Stub.restore();
        encodeBase64Stub.restore();
    });
    // METR-38254
    it.skip(`sets ${IS_TURBO_APP_BR_KEY}`, () => {
        chai.expect(
            BRINFO_FLAG_GETTERS[IS_TURBO_APP_BR_KEY](
                {
                    yandex: {
                        app: {},
                    },
                } as any,
                counterOpt,
                senderParams,
            ),
        ).to.eq(1);

        chai.expect(
            BRINFO_FLAG_GETTERS[IS_TURBO_APP_BR_KEY](
                {} as any,
                counterOpt,
                senderParams,
            ),
        ).to.eq(null);
    });
});
