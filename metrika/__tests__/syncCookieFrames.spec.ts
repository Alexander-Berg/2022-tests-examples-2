import * as chai from 'chai';
import * as sinon from 'sinon';
import * as dom from '@src/utils/dom';

import * as defer from '@src/utils/defer';
import * as time from '@src/utils/time';
import * as lStorage from '@src/storage/localStorage';
import * as globalUtils from '@src/utils';
import * as events from '@src/utils/events';
import * as global from '@src/storage/global';
import * as object from '@src/utils/object';
import * as string from '@src/utils/string';
import * as array from '@src/utils/array';
import * as syncCookieFrame from '../syncCookieFrame';
import * as utils from '../utils';

import {
    DomainInfo,
    EXP_TIME_SYNC_COOKIE,
    LS_KEY_SYNC_COOKIE,
    SYNC_COOKIE_TIME_DIFF,
} from '../const';

describe('syncCookie middleware Frame mode', () => {
    const sandbox = sinon.createSandbox();
    const win = () => ({} as any as Window);
    let clearDefer: sinon.SinonStub<any, any>;
    let setDefer: sinon.SinonStub<any, any>;

    let globalLocalStorageStub: sinon.SinonStub<any, any>;
    let timeStub: sinon.SinonStub<any, any>;
    let fakePromise: sinon.SinonStub<any, any>;
    let hiddenFrameCreate: sinon.SinonStub<any, any>;
    let hiddenFrameRemove: sinon.SinonStub<any, any>;
    let cEvent: sinon.SinonStub<any, any>;

    let getGlobalStorageStub: sinon.SinonStub<any, any>;

    let saveUnsubscribe: sinon.SinonStub<any, any>;
    let callUnsubscribe: sinon.SinonStub<any, any>;

    const setValLSSpy = sandbox.stub();
    const getValLSSpy = sandbox.stub();
    const setValSpy = sandbox.stub();
    const getValSpy = sandbox.stub();
    const fakeResolve = sandbox.stub();
    const fakeReject = sandbox.stub();
    const fakeEventUnsubscribe = sandbox.stub();
    const fakeEventOn = sandbox.stub();
    fakeEventOn.returns(fakeEventUnsubscribe);
    let testMin: number;

    beforeEach(() => {
        fakePromise = sandbox.stub(globalUtils, 'PolyPromise');
        clearDefer = sandbox.stub(defer, 'clearDefer');
        setDefer = sandbox.stub(defer, 'setDefer');
        setDefer.returns(1);

        hiddenFrameCreate = sandbox.stub(dom, 'hiddenFrameCreate');
        hiddenFrameCreate.returns({} as HTMLIFrameElement);
        hiddenFrameRemove = sandbox.stub(dom, 'hiddenFrameRemove');

        cEvent = sandbox.stub(events, 'cEvent');
        cEvent.returns({
            on: fakeEventOn,
        });
        saveUnsubscribe = sandbox.stub(syncCookieFrame, 'saveUnsubscribe');
        callUnsubscribe = sandbox.stub(syncCookieFrame, 'callUnsubscribe');

        globalLocalStorageStub = sandbox.stub(lStorage, 'globalLocalStorage');
        globalLocalStorageStub.returns({
            setVal: setValLSSpy,
            getVal: getValLSSpy,
        });

        getGlobalStorageStub = sandbox.stub(global, 'getGlobalStorage');
        getGlobalStorageStub.returns({
            setVal: setValSpy,
            getVal: getValSpy,
        });

        timeStub = sandbox.stub(time, 'TimeOne');
        testMin = (Math.random() + 16000) * 100000;
        timeStub.returns(() => testMin);
    });
    afterEach(() => {
        sandbox.restore();
        setValSpy.resetHistory();
        getValSpy.resetHistory();
        setValLSSpy.resetHistory();
        getValLSSpy.resetHistory();
        fakeResolve.resetHistory();
        fakeReject.resetHistory();
        fakeEventOn.resetHistory();
        fakeEventUnsubscribe.resetHistory();
    });

    it('call syncCookieFrame.syncDomains with empty domains list', () => {
        const winInfo = win();
        const domainList: DomainInfo[] = [];

        syncCookieFrame.syncDomains(winInfo, domainList);
        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);
        sinon.assert.calledOnce(fakeResolve);
        sinon.assert.notCalled(hiddenFrameCreate);
    });

    it('call syncCookieFrame.syncDomains with domains no hiddenFrame', () => {
        const winInfo = win();
        const domainList: DomainInfo[] = [
            {
                lsKey: 'key1',
                domain: 'domain1',
            },
        ];
        hiddenFrameCreate.returns(null);
        syncCookieFrame.syncDomains(winInfo, domainList);
        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);
        sinon.assert.notCalled(fakeResolve);
        sinon.assert.calledOnce(fakeReject);
        sinon.assert.calledOnce(hiddenFrameCreate);
    });

    it('call syncCookieFrame.syncDomains with domains', () => {
        const winInfo = win();
        const domainList: DomainInfo[] = [
            {
                lsKey: 'key1',
                domain: 'domain1',
            },
        ];
        syncCookieFrame.syncDomains(winInfo, domainList);
        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);
        sinon.assert.calledOnce(hiddenFrameCreate);
        sinon.assert.calledOnce(saveUnsubscribe);
        sinon.assert.calledOnce(setDefer);
    });

    it('call syncCookieFrame.finalizeSync with true', () => {
        const winInfo = win();
        const domainList: DomainInfo[] = [
            {
                lsKey: 'lskey',
                domain: 'domain',
            },
        ];
        syncCookieFrame.syncDomains(winInfo, domainList);
        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);

        const frameUrl = 'test frame url';
        const callback = sandbox.spy();

        getValLSSpy.returns({});

        syncCookieFrame.finalizeSync(
            winInfo,
            frameUrl,
            callback,
            domainList,
            true,
        );
        sinon.assert.calledWith(
            setValLSSpy,
            LS_KEY_SYNC_COOKIE,
            sinon.match({
                lskey: testMin,
            }),
        );

        sinon.assert.calledOnce(clearDefer);
        sinon.assert.calledOnce(callUnsubscribe);
        sinon.assert.calledOnce(hiddenFrameRemove);
    });

    it('call syncCookieFrame.finalizeSync with false', () => {
        const winInfo = win();
        const domainList: DomainInfo[] = [
            {
                lsKey: 'lskey',
                domain: 'domain',
            },
        ];
        syncCookieFrame.syncDomains(winInfo, domainList);
        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);

        const frameUrl = 'test frame url';
        const callback = sandbox.spy();

        getValLSSpy.returns({});

        syncCookieFrame.finalizeSync(
            winInfo,
            frameUrl,
            callback,
            domainList,
            false,
        );
        sinon.assert.calledWith(
            setValLSSpy,
            LS_KEY_SYNC_COOKIE,
            sinon.match({
                lskey: testMin - (EXP_TIME_SYNC_COOKIE - SYNC_COOKIE_TIME_DIFF),
            }),
        );

        sinon.assert.calledOnce(clearDefer);
        sinon.assert.calledOnce(callUnsubscribe);
        sinon.assert.calledOnce(hiddenFrameRemove);
    });

    it('call syncCookieFrame.genOnMessage with wrong message', () => {
        const winInfo = win();
        const domainList: DomainInfo[] = [
            {
                lsKey: 'lskey',
                domain: 'domain',
            },
        ];
        syncCookieFrame.syncDomains(winInfo, domainList);
        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);

        const frameUrl = 'test frame url';
        const callback = sandbox.spy();
        const globalStorage = getGlobalStorageStub();
        const getPath = sandbox.stub(object, 'getPath');
        getPath.returns(null);
        const isString = sandbox.stub(string, 'isString');
        isString.returns(false);
        syncCookieFrame.genOnMessage(
            winInfo,
            frameUrl,
            callback,
            [],
            globalStorage,
            undefined,
            {},
        );
        sinon.assert.calledWith(isString, null);
    });
    it('call syncCookieFrame.genOnMessage with error message', () => {
        const winInfo = win();
        const domainList: DomainInfo[] = [
            {
                lsKey: 'lskey',
                domain: 'domain',
            },
        ];
        syncCookieFrame.syncDomains(winInfo, domainList);
        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);

        const frameUrl = 'test frame url';
        const callback = sandbox.spy();
        const globalStorage = getGlobalStorageStub();
        const getPath = sandbox.stub(object, 'getPath');
        getPath.returns('sc.image*http://domain/sync_cookie_image_check*0');
        const isString = sandbox.stub(string, 'isString');
        isString.returns(true);
        const cForEach = sandbox.stub(array, 'cForEach');
        cForEach.returns([]);
        const cFilter = sandbox.stub(array, 'cFilter');
        const getCookieState = sandbox.stub(utils, 'getCookieState');
        getCookieState.returns([]);
        const finalizeSyncStub = sandbox.stub(syncCookieFrame, 'finalizeSync');
        cFilter.returns([]);
        syncCookieFrame.genOnMessage(
            winInfo,
            frameUrl,
            callback,
            [],
            globalStorage,
            undefined,
            {},
        );
        chai.expect(finalizeSyncStub.getCall(0).args[4]).to.equal(false);
    });

    it('call syncCookieFrame.genOnMessage with error message', () => {
        const finalizeSyncStub = sandbox.stub(syncCookieFrame, 'finalizeSync');
        const winInfo = win();
        const domainList: DomainInfo[] = [
            {
                lsKey: 'lskey',
                domain: 'domain',
            },
        ];
        syncCookieFrame.syncDomains(winInfo, domainList);
        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);

        const frameUrl = 'test frame url';
        const callback = sandbox.spy();
        const globalStorage = getGlobalStorageStub();
        const getPath = sandbox.stub(object, 'getPath');
        getPath.returns('sc.image*http://domain/sync_cookie_image_check*0');
        const isString = sandbox.stub(string, 'isString');
        isString.returns(true);
        const cForEach = sandbox.stub(array, 'cForEach');
        cForEach.returns([]);
        const cFilter = sandbox.stub(array, 'cFilter');
        const getCookieState = sandbox.stub(utils, 'getCookieState');
        getCookieState.returns([]);
        cFilter.returns([]);
        syncCookieFrame.genOnMessage(
            winInfo,
            frameUrl,
            callback,
            [],
            globalStorage,
            undefined,
            {},
        );
        chai.expect(finalizeSyncStub.getCall(0).args[4]).to.equal(false);
    });

    it('call syncCookieFrame.genOnMessage with ok message', () => {
        const winInfo = win();
        const domainList: DomainInfo[] = [
            {
                lsKey: 'lskey',
                domain: 'domain',
            },
        ];
        const finalizeSyncStub = sandbox.stub(syncCookieFrame, 'finalizeSync');
        syncCookieFrame.syncDomains(winInfo, domainList);
        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);

        const frameUrl = 'test frame url';
        const callback = sandbox.spy();
        const globalStorage = getGlobalStorageStub();
        const getPath = sandbox.stub(object, 'getPath');
        getPath.returns('sc.image*http://domain/sync_cookie_image_check*1');
        const isString = sandbox.stub(string, 'isString');
        isString.returns(true);
        const cForEach = sandbox.stub(array, 'cForEach');
        cForEach.returns([]);
        const cFilter = sandbox.stub(array, 'cFilter');
        const getCookieState = sandbox.stub(utils, 'getCookieState');
        getCookieState.returns([]);
        cFilter.returns([]);
        syncCookieFrame.genOnMessage(
            winInfo,
            frameUrl,
            callback,
            [],
            globalStorage,
            undefined,
            {},
        );
        chai.expect(finalizeSyncStub.getCall(0).args[4]).to.equal(true);
    });
});
