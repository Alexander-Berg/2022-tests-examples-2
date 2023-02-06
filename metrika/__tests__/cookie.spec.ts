import * as sinon from 'sinon';
import {
    isCookieAllowed,
    YANX_GDPR_COOKIE,
    YANX_GDPR_POPUP_COOKIE,
} from '@src/middleware/gdpr/cookie';
import { ENABLED_COOKIE_KEY } from '@src/storage/cookie/const';
import * as chai from 'chai';
import {
    GDPR_ALLOW_COOKIE_LIST,
    GDPR_ANALYTIC,
    GDPR_DISABLE_ALL,
    GDPR_ENABLE_ALL,
} from '@src/middleware/gdpr/status';
import * as dataLayer from '@src/utils/dataLayerObserver';

describe('gdpr cookie', () => {
    const win = {} as Window;
    let cookies: Record<string, any>;
    const getCookie = (ctx: Window, name: string) => {
        return cookies[name];
    };

    const sandbox = sinon.createSandbox();
    let getDataLayerStub: sinon.SinonStub;

    beforeEach(() => {
        cookies = {};
        getDataLayerStub = sandbox.stub(dataLayer, 'getInnerDataLayer');
        getDataLayerStub.returns([]);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('is tech allowed ', () => {
        delete cookies[YANX_GDPR_COOKIE];

        [YANX_GDPR_COOKIE, YANX_GDPR_POPUP_COOKIE, ENABLED_COOKIE_KEY].forEach(
            (item) => {
                chai.expect(isCookieAllowed(win, getCookie, item)).to.be.equal(
                    true,
                );
            },
        );
    });
    it('is allowed with analytic gdpr value', () => {
        [GDPR_ENABLE_ALL, GDPR_ANALYTIC].forEach((gdprValue) => {
            cookies[YANX_GDPR_COOKIE] = gdprValue;

            const cookieName = `name${gdprValue}`;

            chai.expect(
                isCookieAllowed(win, getCookie, cookieName),
            ).to.be.equal(true);
            delete cookies[cookieName];
        });

        [GDPR_DISABLE_ALL, '3'].forEach((gdprValue) => {
            cookies[YANX_GDPR_COOKIE] = gdprValue;

            const cookieName = `name${gdprValue}`;
            chai.expect(
                isCookieAllowed(win, getCookie, cookieName),
            ).to.be.equal(false);
        });
    });

    it('allowed analytics', () => {
        getDataLayerStub.returns([
            {
                [dataLayer.INNER_DATA_LAYER_NAMESPACE]: {
                    [dataLayer.INNER_DATA_LAYER_TYPE_KEY]:
                        GDPR_ALLOW_COOKIE_LIST[0],
                },
            },
        ]);

        const cookieName = `testCookie`;

        chai.expect(isCookieAllowed(win, getCookie, cookieName)).to.be.equal(
            true,
        );
    });
});
