import * as chai from 'chai';
import * as sinon from 'sinon';
import * as loc from '@src/utils/location';
import * as brow from '@src/utils/browser';
import * as time from '@src/utils/time';
import * as transport from '@src/transport';
import * as sender from '@src/sender/default';
import { browserInfo } from '@src/utils/browserInfo';
import { cKeys } from '@src/utils/object';
import { cForEach } from '@src/utils/array';
import * as lStorage from '@src/storage/localStorage';
import * as glStorage from '@src/storage/global';
import { PAGE_VIEW_BR_KEY } from '@src/providers/hit/const';
import {
    EURO_FEATURE,
    FOR_UA_FEATURE,
    PREPROD_FEATURE,
} from '@generated/features';
import * as inject from '@inject';
import {
    LS_KEY_SYNC_COOKIE,
    EXP_TIME_SYNC_COOKIE,
    SYNC_COOKIE_TIME_DIFF,
    SYNC_GS_FLAG,
} from '../const';
import { syncCookie } from '../syncCookie';
import * as middle from '../../types';

describe('syncCookie middleware', () => {
    const counterOptions: any = { id: 123 };
    const ls: Record<string, any> = {};
    const sandbox = sinon.createSandbox();
    const win = () => ({} as any as Window);
    let isSyncDomainStub: sinon.SinonStub<any, any>;
    let getLanguageStub: sinon.SinonStub<any, any>;
    let getLocationStub: sinon.SinonStub<any, any>;
    let globalStorageStub: sinon.SinonStub<any, any>;
    let globalLocalStorageStub: sinon.SinonStub<any, any>;
    let timeStub: sinon.SinonStub<any, any>;
    let fakeMiddleStub: sinon.SinonStub<any, any>;
    let transportStub: sinon.SinonStub<any, any>;
    let senderStub: sinon.SinonStub<any, any>;
    let isIframeStub: sinon.SinonStub<any, any>;
    let isITPSpy: sinon.SinonStub<any, any>;
    let isFFSpy: sinon.SinonStub<any, any>;

    let middleware: middle.Middleware;

    const setValSpy = sandbox.stub();
    const getValSpy = sandbox.stub();
    const setValLSSpy = sandbox.stub();
    const getValLSSpy = sandbox.stub();
    const fakeSpy = sandbox.stub();
    let testMin: number;

    beforeEach(() => {
        testMin = (Math.random() + 16000) * 100000;
        cForEach((key: string) => delete ls[key], cKeys(ls));
        fakeMiddleStub = sandbox.stub(middle, 'fakeProvider');
        fakeMiddleStub.value([fakeSpy]);
        globalLocalStorageStub = sandbox.stub(lStorage, 'globalLocalStorage');
        globalLocalStorageStub.returns({
            setVal: setValLSSpy,
            getVal: getValLSSpy,
        });
        globalStorageStub = sandbox.stub(glStorage, 'getGlobalStorage');
        globalStorageStub.returns({
            setVal: setValSpy,
            getVal: getValSpy,
        });
        isSyncDomainStub = sandbox.stub(loc, 'isSyncDomain');
        senderStub = sandbox.stub(sender, 'useDefaultSender');
        getLocationStub = sandbox.stub(loc, 'getLocation');
        getLanguageStub = sandbox.stub(brow, 'getLanguage');
        isIframeStub = sandbox.stub(brow, 'isIframe');
        isIframeStub.returns(false);
        timeStub = sandbox.stub(time, 'TimeOne');
        timeStub.returns(() => testMin);
        transportStub = sandbox.stub(transport, 'getTransportList');
        isITPSpy = sandbox.stub(brow, 'isITP');
        isITPSpy.returns(false);
        isFFSpy = sandbox.stub(brow, 'isFF');
        isFFSpy.returns(false);
        sandbox.stub(inject, 'flags').value({
            ...inject.flags,
            [EURO_FEATURE]: false,
            [FOR_UA_FEATURE]: false,
            [PREPROD_FEATURE]: false,
        });
    });
    afterEach(() => {
        sandbox.restore();
        setValLSSpy.resetHistory();
        getValLSSpy.resetHistory();
        fakeSpy.resetHistory();
    });

    it('get sync domains if catch', (done) => {
        const winInfo = win();
        isSyncDomainStub.withArgs(winInfo).returns(true);
        getValSpy.withArgs(SYNC_GS_FLAG).returns(false);
        getLocationStub.withArgs(winInfo).returns({
            hostname: 'yandex.ru',
            href: 'https://yandex.ru',
        });
        const preDefLsState = {
            ru: testMin + SYNC_COOKIE_TIME_DIFF,
        };
        getValLSSpy.returns(preDefLsState);
        getLanguageStub.withArgs(winInfo).returns('tr');
        const transportList = [] as const;
        fakeSpy.returns(Promise.resolve());
        transportStub.withArgs(winInfo).returns(transportList);
        senderStub.returns(() => {
            return Promise.reject(new Error('Transport fail'));
        });
        middleware = syncCookie(winInfo, 'h', counterOptions);
        middleware.beforeRequest!(
            {
                brInfo: browserInfo({
                    [PAGE_VIEW_BR_KEY]: 1,
                }),
            },
            () => {
                sinon.assert.calledOnce(senderStub);
                sinon.assert.calledWith(
                    setValLSSpy,
                    LS_KEY_SYNC_COOKIE,
                    sinon.match({
                        'com.tr':
                            testMin -
                            (EXP_TIME_SYNC_COOKIE - SYNC_COOKIE_TIME_DIFF),
                    }),
                );
                done();
            },
        );
        sinon.assert.calledOnce(fakeSpy);
    });

    it('get sync domains', (done) => {
        const winInfo = win();
        const locInfo = {
            hostname: 'yandex.ru',
            href: 'https://yandex.ru',
        };
        const preDefLsState = {
            ru: testMin + SYNC_COOKIE_TIME_DIFF,
        };
        getValLSSpy.returns(preDefLsState);
        isSyncDomainStub.withArgs(winInfo).returns(true);
        getLocationStub.withArgs(winInfo).returns(locInfo);
        getLanguageStub.withArgs(winInfo).returns('tr');
        const transportList = [] as const;
        transportStub.withArgs(winInfo).returns(transportList);
        fakeSpy.returns(Promise.resolve());
        senderStub.returns(() => {
            return Promise.resolve();
        });
        middleware = syncCookie(winInfo, 'h', counterOptions);
        middleware.beforeRequest!(
            {
                brInfo: browserInfo({
                    [PAGE_VIEW_BR_KEY]: 1,
                }),
            },
            () => {
                sinon.assert.calledOnce(senderStub);
                sinon.assert.calledWith(setValLSSpy, LS_KEY_SYNC_COOKIE, {
                    ...preDefLsState,
                    'com.tr': testMin,
                });
                done();
            },
        );
        sinon.assert.calledOnce(fakeSpy);
    });
    it('sync partner domain', (done) => {
        const winInfo = win();
        const locInfo = {
            hostname: 'plus.kinopoisk.ru',
            href: 'https://yandex.ru',
        };
        const preDefLsState = {
            'com.tr': testMin + SYNC_COOKIE_TIME_DIFF,
        };
        getValLSSpy.returns(preDefLsState);
        isSyncDomainStub.withArgs(winInfo).returns(true);
        getLocationStub.withArgs(winInfo).returns(locInfo);
        getLanguageStub.withArgs(winInfo).returns('tr');
        const transportList = [] as const;
        transportStub.withArgs(winInfo).returns(transportList);
        fakeSpy.returns(Promise.resolve());
        senderStub.returns(() => {
            return Promise.resolve();
        });
        middleware = syncCookie(winInfo, 'h', counterOptions);
        middleware.beforeRequest!(
            {
                brInfo: browserInfo({
                    [PAGE_VIEW_BR_KEY]: 1,
                }),
            },
            () => {
                sinon.assert.calledOnce(senderStub);
                sinon.assert.calledWith(setValLSSpy, LS_KEY_SYNC_COOKIE, {
                    ...preDefLsState,
                    'mc.kinopoisk.ru': testMin,
                });
                done();
            },
        );
        sinon.assert.calledOnce(fakeSpy);
    });

    it('get domain list', () => {
        const winInfo = win();
        isSyncDomainStub.returns(true);
        getLocationStub.withArgs(winInfo).returns({
            hostname: 'plus.kinopoisk.ru',
        });
        getLanguageStub.withArgs(winInfo).returns('ru');
        const preDefLsState = {
            'mc.kinopoisk.ru': testMin + SYNC_COOKIE_TIME_DIFF,
        };
        getValLSSpy.returns(preDefLsState);
        middleware = syncCookie(winInfo, 'h', counterOptions);
        middleware.beforeRequest!(
            {
                brInfo: browserInfo({
                    [PAGE_VIEW_BR_KEY]: 1,
                }),
            },
            () => {
                sinon.assert.calledWith(
                    setValLSSpy,
                    LS_KEY_SYNC_COOKIE,
                    preDefLsState,
                );
            },
        );
        sinon.assert.calledOnce(getValLSSpy);
    });
    // для тестов мы собираем европейскую версию
    // в METR-39817 в европейской версии мы включили
    // синк на всех доменах
    it('skip if ru lang in ru site', (done) => {
        const winInfo = win();
        fakeSpy.returns(Promise.resolve());
        senderStub.returns(() => {
            return Promise.resolve();
        });
        isSyncDomainStub.returns(true);
        getLocationStub.withArgs(winInfo).returns({
            hostname: 'yandex.ru',
        });
        getLanguageStub.withArgs(winInfo).returns('kss');
        getValLSSpy.returns({});
        middleware = syncCookie(winInfo, 'h', counterOptions);
        middleware.beforeRequest!(
            {
                brInfo: browserInfo({
                    [PAGE_VIEW_BR_KEY]: 1,
                }),
            },
            () => {
                sinon.assert.calledWith(getValLSSpy, LS_KEY_SYNC_COOKIE, {});
                done();
            },
        );
        sinon.assert.calledOnce(getValLSSpy);
    });
    // для тестов мы собираем европейскую версию
    // в METR-39817 в европейской версии мы включили
    // синк на всех доменах
    it('skip if it not pageview', () => {
        const winInfo = win();
        getLocationStub.withArgs(winInfo).returns({
            hostname: 'plus.ru',
        });
        middleware = syncCookie(winInfo, 'h', counterOptions);
        middleware.beforeRequest!({}, () => {
            sinon.assert.calledWith(globalStorageStub, winInfo);
        });
        sinon.assert.calledWith(isSyncDomainStub, winInfo);
    });
    it('block in ITPSafari', () => {
        const winInfo = win();
        isITPSpy.returns(true);
        middleware = syncCookie(winInfo, 'h', counterOptions);
        chai.expect(middleware.beforeRequest).to.be.undefined;
        chai.expect(middleware.afterRequest).to.be.undefined;
    });
    it('block in Firefox', () => {
        const winInfo = win();
        isFFSpy.returns(true);
        middleware = syncCookie(winInfo, 'h', counterOptions);
        chai.expect(middleware.beforeRequest).to.be.undefined;
        chai.expect(middleware.afterRequest).to.be.undefined;
    });
});
