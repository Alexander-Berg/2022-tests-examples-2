import * as sinon from 'sinon';
import {
    gdpr,
    GDPR_EXPIRES,
    GRDPR_BR_KEY,
    YANX_LOGIN_COOKIE,
} from '@src/middleware/gdpr';
import * as dataLayer from '@src/utils/dataLayerObserver';
import * as cookie from '@src/storage/cookie';
import * as location from '@src/utils/location';
import * as global from '@src/storage/global';
import {
    GDPR_COOKIE_SUCCESS,
    GDPR_DISABLE_ALL,
    GDPR_ENABLE_ALL,
    GDPR_EU_SKIP,
    GDPR_SKIP_DOMAIN,
    GDPR_SKIP_LOGIN,
    GDPR_SKIP_WV,
} from '@src/middleware/gdpr/status';
import {
    INNER_DATA_LAYER_NAMESPACE,
    INNER_DATA_LAYER_TYPE_KEY,
} from '@src/utils/dataLayerObserver';
import * as browser from '@src/utils/browser';
import * as iterator from '@src/utils/async/iterator';
import * as executor from '@src/utils/async/executor';
import * as fake from '@src/middleware/types';
import { FAKE_HIT_PARAMS_KEY } from '@src/providers/fakeHit/const';
import * as chai from 'chai';
import {
    YANX_GDPR_COOKIE,
    YANX_GDPR_POPUP_COOKIE,
} from '@src/middleware/gdpr/cookie';
import * as iframe from '../iframe';
import * as popup from '../popUp';
import * as params from '../params';

describe('gdpr', () => {
    const sandbox = sinon.createSandbox();
    const win = {} as any;
    const provider = 'p';
    const counterOptions = {} as any;
    const popupGdprValue = '2';
    let senderParams = {} as any;
    let testDataLayer: any;
    let beforeRequest: Exclude<
        ReturnType<typeof gdpr>['beforeRequest'],
        undefined
    >;

    let brInfoSetValSpy: sinon.SinonSpy;
    let cookieGetValStub: sinon.SinonStub;
    let cookieSetValSpy: sinon.SinonSpy;
    let cookieDelValSpy: sinon.SinonSpy;
    let initIframeStub: sinon.SinonStub;
    let GDPRIframeStub: sinon.SinonStub;
    let GDPRPopUpStub: sinon.SinonStub;
    let globalConfigSetValStub: sinon.SinonStub;
    let isWebViewStub: sinon.SinonStub;
    let isIframeStub: sinon.SinonStub;
    let isYandexStub: sinon.SinonStub;
    let getInnerDataLayerStub: sinon.SinonStub;
    let fakeHitStub: sinon.SinonStub;

    beforeEach(() => {
        testDataLayer = [];

        getInnerDataLayerStub = sandbox
            .stub(dataLayer, 'getInnerDataLayer')
            .callsFake(() => testDataLayer);
        sandbox.stub(dataLayer, 'pushToDataLayer').callsFake((arr, event) => {
            arr.push({
                [INNER_DATA_LAYER_NAMESPACE]: {
                    [INNER_DATA_LAYER_TYPE_KEY]: event,
                },
            });
        });

        cookieGetValStub = sandbox.stub();
        cookieSetValSpy = sandbox.spy();
        cookieDelValSpy = sandbox.spy();
        sandbox.stub(cookie, 'cookieStorage').callsFake(
            () =>
                ({
                    getVal: cookieGetValStub,
                    setVal: cookieSetValSpy,
                    delVal: cookieDelValSpy,
                } as any),
        );

        isYandexStub = sandbox
            .stub(location, 'isYandexOwnerDomain')
            .returns(true);
        sandbox.stub(location, 'getLocation').returns({ href: '' } as any);
        globalConfigSetValStub = sandbox.stub();
        sandbox.stub(global, 'getGlobalStorage').callsFake(
            () =>
                ({
                    getVal: globalConfigSetValStub,
                    setVal: () => {},
                } as any),
        );
        brInfoSetValSpy = sandbox.spy();
        senderParams = {
            brInfo: {
                setVal: brInfoSetValSpy,
            },
        };
        isWebViewStub = sandbox.stub(browser, 'isSafariWebView');
        sandbox.stub(browser, 'isAndroidWebView');
        isIframeStub = sandbox.stub(browser, 'isIframe');
        initIframeStub = sandbox.stub(iframe, 'initIframe');
        GDPRIframeStub = sandbox
            .stub(iframe, 'GDPRIframe')
            .returns(Promise.resolve({ value: GDPR_ENABLE_ALL }));
        GDPRPopUpStub = sandbox
            .stub(popup, 'GDPRPopUp')
            .returns(
                Promise.resolve({ value: popupGdprValue, isSession: true }),
            );
        sandbox.stub(params, 'sendGDPRParams').returns();

        sandbox.stub(iterator, 'iterForOf').callsFake(((list: Function[]) => {
            list.map((fn: Function) => fn());
            list.splice(0, list.length);
        }) as any);
        sandbox.stub(executor, 'executeIterator').returns((() => {}) as any);
        fakeHitStub = sandbox
            .stub(fake, 'fakeProvider')
            .value([
                () => Promise.resolve({ [FAKE_HIT_PARAMS_KEY]: { eu: 1 } }),
            ]);

        const middleware = gdpr(win, provider, counterOptions);
        beforeRequest =
            middleware.beforeRequest ||
            (() => {
                chai.assert.fail('empty beforeRequest');
            });
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('skip check if optout', () => {
        gdpr(win, provider, {
            id: 1,
            counterType: '0',
            yaDisableGDPR: true,
        }).beforeRequest!(senderParams, () => {});
        sinon.assert.notCalled(getInnerDataLayerStub);
    });
    it('has gdpr cookie', (done) => {
        cookieGetValStub.withArgs(YANX_GDPR_COOKIE).returns('0');

        beforeRequest(senderParams, done);
        sinon.assert.calledWith(
            brInfoSetValSpy,
            GRDPR_BR_KEY,
            `${GDPR_COOKIE_SUCCESS}-0`,
        );
    });

    it('has yandex login', (done) => {
        cookieGetValStub.withArgs(YANX_LOGIN_COOKIE).returns('login');

        beforeRequest(senderParams, done);
        sinon.assert.calledWith(
            cookieSetValSpy,
            YANX_GDPR_COOKIE,
            GDPR_ENABLE_ALL,
            GDPR_EXPIRES,
        );
        sinon.assert.calledWith(
            brInfoSetValSpy,
            GRDPR_BR_KEY,
            `${GDPR_SKIP_LOGIN}-${GDPR_ENABLE_ALL}`,
        );
    });

    it('skip not yandex domain', (done) => {
        isYandexStub.returns(false);

        beforeRequest(senderParams, done);
        sinon.assert.calledWith(
            brInfoSetValSpy,
            GRDPR_BR_KEY,
            `${GDPR_SKIP_DOMAIN}`,
        );
    });

    it('skip web view', (done) => {
        isWebViewStub.returns(true);

        beforeRequest(senderParams, done);
        sinon.assert.calledWith(
            brInfoSetValSpy,
            GRDPR_BR_KEY,
            `${GDPR_SKIP_WV}`,
        );
    });

    it('iframe', (done) => {
        isIframeStub.returns(true);

        beforeRequest(senderParams, () => {
            sinon.assert.calledWith(
                cookieSetValSpy.getCall(0),
                YANX_GDPR_POPUP_COOKIE,
                GDPR_DISABLE_ALL,
            );

            sinon.assert.called(initIframeStub);
            sinon.assert.called(GDPRIframeStub);

            sinon.assert.calledWith(cookieDelValSpy, YANX_GDPR_POPUP_COOKIE);

            sinon.assert.calledWith(
                cookieSetValSpy.getCall(1),
                YANX_GDPR_COOKIE,
                GDPR_ENABLE_ALL,
                GDPR_EXPIRES,
            );
            done();
        });
    });

    it('show popup - eu from fake hit', (done) => {
        beforeRequest(senderParams, () => {
            sinon.assert.calledWith(
                cookieSetValSpy.getCall(0),
                YANX_GDPR_POPUP_COOKIE,
                GDPR_DISABLE_ALL,
            );

            sinon.assert.called(initIframeStub);
            sinon.assert.called(GDPRPopUpStub);

            sinon.assert.calledWith(cookieDelValSpy, YANX_GDPR_POPUP_COOKIE);

            sinon.assert.calledWith(
                cookieSetValSpy.getCall(1),
                YANX_GDPR_COOKIE,
                popupGdprValue,
            );
            done();
        });
    });

    it('not eu', (done) => {
        fakeHitStub.value([
            () => Promise.resolve({ [FAKE_HIT_PARAMS_KEY]: { eu: 0 } }),
        ]);
        cookieGetValStub.withArgs(YANX_GDPR_COOKIE).onSecondCall().returns('0');

        beforeRequest(senderParams, () => {
            sinon.assert.calledWith(
                cookieSetValSpy.getCall(0),
                YANX_GDPR_COOKIE,
                GDPR_ENABLE_ALL,
                undefined,
            );
            sinon.assert.calledWith(
                brInfoSetValSpy,
                GRDPR_BR_KEY,
                `${GDPR_EU_SKIP}-${GDPR_ENABLE_ALL}`,
            );

            done();
        });
    });
});
