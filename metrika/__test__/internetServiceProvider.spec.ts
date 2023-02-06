import * as countOpt from '@src/utils/counterOptions';
import * as sinon from 'sinon';
import * as browser from '@src/utils/browser';
import * as location from '@src/utils/location';
import * as counterSettings from '@src/utils/counterSettings';
import * as globalUtils from '@src/utils';
import * as defer from '@src/utils/defer';
import * as dom from '@src/utils/dom';
import * as events from '@src/utils/events';
import { ACTION_FRAME, ACTION_IMAGES, ACTION_IMAGE } from '@src/utils/dom';
import chai from 'chai';
import { MEGAFON_KEY } from '../const';
import * as utils from '../utils';
import * as internetServiceProvider from '../internetServiceProvider';

describe('isp provider', () => {
    const { useISP, onMessage, makeIframeRequest } = internetServiceProvider;
    const sandbox = sinon.createSandbox();
    const hashStub = 1234;
    const maskStub = '1234';
    const testHost = 'test.com';
    const counterOptions: countOpt.CounterOptions = {
        counterType: '0',
        id: hashStub,
    };
    const counterKey = 'counterKey';
    const hitInfo: any = {
        settings: {
            pcs: '0',
            eu: false,
        },
        userData: {},
    };
    const messageEvent = { source: {}, data: '' } as any;
    const win = {} as any;
    const stateObj = {} as Record<string, number>;
    const successStatus = '1';
    const failStatus = '0';
    const messageIframeEvent = `${ACTION_FRAME}*${testHost}*${successStatus}`;
    const messageImageSuccessEvent = `${ACTION_IMAGE}*${testHost}*${successStatus}`;
    const messageImageFailEvent = `${ACTION_IMAGE}*${testHost}*${failStatus}`;
    const messageImageEvent = `${ACTION_IMAGE}*@${testHost}*${successStatus}`;

    let fakeResolve: sinon.SinonStub<any, any>;
    let fakeReject: sinon.SinonStub<any, any>;
    let fakePromise: sinon.SinonStub<any, any>;
    let fakeOnMessageCallback: sinon.SinonStub<any, any>;
    let fakePostMessage: sinon.SinonStub<any, any>;
    let setDefer: sinon.SinonStub<any, any>;
    let hiddenFrameCreate: sinon.SinonStub<any, any>;
    let hiddenFrameRemove: sinon.SinonStub<any, any>;
    let cEvent: sinon.SinonStub<any, any>;
    let fakeEventUnsubscribe: sinon.SinonStub<any, any>;
    let fakeEvent: sinon.SinonStub<any, any>;
    let makeRequestStub: sinon.SinonStub<any, any>;
    let getSateStub: sinon.SinonStub<any, any>;
    let isITPStub: sinon.SinonStub<any, any>;
    let isCSPEnabledStub: sinon.SinonStub<any, any>;
    let isYandexOwnerDomainStub: sinon.SinonStub<any, any>;
    let getSettingsStub: sinon.SinonStub<any, any>;
    let getFNVHashStub: sinon.SinonStub<any, any>;
    let encodeUidForMFStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        fakeResolve = sandbox.stub();
        fakeReject = sandbox.stub();
        fakeEventUnsubscribe = sandbox.stub();
        fakeEvent = sandbox.stub().returns(fakeEventUnsubscribe);
        fakeOnMessageCallback = sandbox.stub();
        fakePostMessage = sandbox.stub();
        makeRequestStub = sandbox
            .stub(internetServiceProvider, 'makeIframeRequest')
            .returns(Promise.resolve());
        getSateStub = sandbox.stub(utils, 'getState');
        getSateStub.returns(stateObj);
        getSettingsStub = sandbox
            .stub(counterSettings, 'getCounterSettings')
            .callsFake((_, __, fn) => {
                return new Promise((resolve) => {
                    return resolve(fn(hitInfo as any));
                });
            });

        isCSPEnabledStub = sandbox.stub(counterSettings, 'isCSPEnabled');
        isYandexOwnerDomainStub = sandbox.stub(location, 'isYandexOwnerDomain');
        isITPStub = sandbox.stub(browser, 'isITP');

        fakePromise = sandbox.stub(globalUtils, 'PolyPromise');
        setDefer = sandbox.stub(defer, 'setDefer');
        setDefer.returns(1);

        hiddenFrameCreate = sandbox.stub(dom, 'hiddenFrameCreate');
        hiddenFrameCreate.returns({} as HTMLIFrameElement);
        hiddenFrameRemove = sandbox.stub(dom, 'hiddenFrameRemove');

        cEvent = sandbox.stub(events, 'cEvent');
        cEvent.returns({
            on: fakeEvent,
        });

        getFNVHashStub = sandbox.stub(utils, 'getFNVHash').returns(hashStub);
        encodeUidForMFStub = sandbox
            .stub(utils, 'encodeUidForMF')
            .returns([maskStub, maskStub]);
        sandbox.stub(countOpt, 'getCounterKey').returns(counterKey);
        messageEvent.source.postMessage = fakePostMessage;
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('useISP: not make request without provider', () => {
        useISP(win, counterOptions);

        sinon.assert.calledOnce(getSettingsStub);
        sinon.assert.notCalled(isITPStub);
        sinon.assert.notCalled(getFNVHashStub);
        sinon.assert.notCalled(encodeUidForMFStub);
        sinon.assert.notCalled(makeRequestStub);
    });
    it('useISP: not make request without ITP', () => {
        hitInfo.settings[MEGAFON_KEY] = 1;
        useISP(win, counterOptions);

        sinon.assert.calledOnce(getSettingsStub);
        sinon.assert.calledOnce(isITPStub);
        sinon.assert.notCalled(getFNVHashStub);
        sinon.assert.notCalled(encodeUidForMFStub);
        sinon.assert.notCalled(makeRequestStub);
    });
    it('useISP: not make request with csp', () => {
        hitInfo.settings[MEGAFON_KEY] = 1;
        isCSPEnabledStub.returns(true);
        isITPStub.returns(true);
        useISP(win, counterOptions);

        sinon.assert.calledOnce(getSettingsStub);
        sinon.assert.calledOnce(isITPStub);
        sinon.assert.notCalled(getFNVHashStub);
        sinon.assert.notCalled(encodeUidForMFStub);
        sinon.assert.notCalled(makeRequestStub);
    });

    it('useISP: make request with csp on yandex domain', () => {
        hitInfo.settings[MEGAFON_KEY] = 1;
        isCSPEnabledStub.returns(true);
        isYandexOwnerDomainStub.returns(true);
        isITPStub.returns(true);
        useISP(win, counterOptions);

        sinon.assert.calledOnce(getSettingsStub);
        sinon.assert.calledOnce(isITPStub);
        sinon.assert.calledOnce(getFNVHashStub);
        sinon.assert.calledWith(getFNVHashStub, win, counterOptions);
        sinon.assert.calledOnce(encodeUidForMFStub);
        sinon.assert.calledWith(encodeUidForMFStub, win, counterOptions);
        sinon.assert.calledOnce(makeRequestStub);
    });

    it('useISP: make request without csp', () => {
        hitInfo.settings[MEGAFON_KEY] = 1;
        isITPStub.returns(true);
        useISP(win, counterOptions);

        sinon.assert.calledOnce(getSettingsStub);
        sinon.assert.calledOnce(isITPStub);
        sinon.assert.calledOnce(getFNVHashStub);
        sinon.assert.calledWith(getFNVHashStub, win, counterOptions);
        sinon.assert.calledOnce(encodeUidForMFStub);
        sinon.assert.calledWith(encodeUidForMFStub, win, counterOptions);
        sinon.assert.calledOnce(makeRequestStub);
    });

    it('onMessage: without data', () => {
        onMessage(win, testHost, fakeOnMessageCallback, messageEvent);

        sinon.assert.notCalled(fakePostMessage);
        sinon.assert.notCalled(fakeOnMessageCallback);
    });

    it('onMessage: with frame actionType', () => {
        messageEvent.data = messageIframeEvent;
        onMessage(win, testHost, fakeOnMessageCallback, messageEvent);

        sinon.assert.calledOnce(fakePostMessage);
        sinon.assert.calledWith(
            fakePostMessage,
            `${ACTION_IMAGES}*${testHost}`,
            '*',
        );
        sinon.assert.notCalled(fakeOnMessageCallback);
    });

    it('onMessage: with success image actionType', () => {
        messageEvent.data = messageImageSuccessEvent;
        onMessage(win, testHost, fakeOnMessageCallback, messageEvent);

        sinon.assert.notCalled(fakePostMessage);
        sinon.assert.calledOnce(fakeOnMessageCallback);
        sinon.assert.calledWith(fakeOnMessageCallback, successStatus);
    });

    it('onMessage: with fail image actionType', () => {
        messageEvent.data = messageImageFailEvent;
        onMessage(win, testHost, fakeOnMessageCallback, messageEvent);

        sinon.assert.notCalled(fakePostMessage);
        sinon.assert.calledOnce(fakeOnMessageCallback);
        sinon.assert.calledWith(fakeOnMessageCallback, failStatus);
    });

    it('onMessage: with different image actionType', () => {
        messageEvent.data = messageImageEvent;
        onMessage(win, testHost, fakeOnMessageCallback, messageEvent);

        sinon.assert.notCalled(fakePostMessage);
        sinon.assert.notCalled(fakeOnMessageCallback);
    });

    it('makeIframeRequest: reject without iframe', () => {
        hiddenFrameCreate.returns(false);
        makeIframeRequest(win, testHost);

        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);
        sinon.assert.calledOnce(fakePromise);

        sinon.assert.calledOnce(hiddenFrameCreate);
        sinon.assert.notCalled(hiddenFrameRemove);

        sinon.assert.notCalled(cEvent);
        sinon.assert.notCalled(fakeEventUnsubscribe);

        sinon.assert.notCalled(setDefer);

        sinon.assert.notCalled(fakeResolve);
        sinon.assert.calledOnce(fakeReject);
    });

    it('makeIframeRequest: reject on timeout', () => {
        setDefer.callsFake((_ctx, fn) => fn());
        makeIframeRequest(win, testHost);

        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);
        sinon.assert.calledOnce(fakePromise);

        sinon.assert.calledOnce(hiddenFrameCreate);
        sinon.assert.calledOnce(hiddenFrameRemove);

        sinon.assert.calledOnce(cEvent);
        sinon.assert.calledOnce(fakeEventUnsubscribe);

        sinon.assert.calledOnce(setDefer);

        sinon.assert.notCalled(fakeResolve);
        sinon.assert.calledOnce(fakeReject);
    });

    it('makeIframeRequest: reject on bad image request', () => {
        messageEvent.data = messageImageFailEvent;
        makeIframeRequest(win, testHost);

        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);

        const [, event, callback] = fakeEvent.getCall(0).args;
        chai.expect(event).to.deep.equal(['message']);
        callback(messageEvent);

        sinon.assert.calledOnce(fakePromise);

        sinon.assert.calledOnce(hiddenFrameCreate);
        sinon.assert.calledOnce(hiddenFrameRemove);

        sinon.assert.calledOnce(cEvent);
        sinon.assert.calledOnce(fakeEventUnsubscribe);

        sinon.assert.calledOnce(setDefer);

        sinon.assert.notCalled(fakeResolve);
        sinon.assert.calledOnce(fakeReject);
    });

    it('makeIframeRequest: resolve on success image request', () => {
        messageEvent.data = messageImageSuccessEvent;
        makeIframeRequest(win, testHost);

        fakePromise.getCall(0).args[0](fakeResolve, fakeReject);

        const [, event, callback] = fakeEvent.getCall(0).args;
        chai.expect(event).to.deep.equal(['message']);
        callback(messageEvent);

        sinon.assert.calledOnce(fakePromise);

        sinon.assert.calledOnce(hiddenFrameCreate);
        sinon.assert.calledOnce(hiddenFrameRemove);

        sinon.assert.calledOnce(cEvent);
        sinon.assert.calledOnce(fakeEventUnsubscribe);

        sinon.assert.calledOnce(setDefer);

        sinon.assert.calledOnce(fakeResolve);
        sinon.assert.notCalled(fakeReject);
    });
});
