import * as chai from 'chai';
import * as sinon from 'sinon';
import * as globalStorage from '@src/storage/global';
import * as cookie from '@src/storage/cookie';
import * as gdprCookie from '@src/middleware/gdpr/cookie';
import { isVisitColorWhite, VISIT_COLOR_COOKIE_NAME } from '../visitColor';

describe('visitColor', () => {
    const sandbox = sinon.createSandbox();
    let checkCookieStub: sinon.SinonStub;
    const fakeGlobalStorage: any = {
        getVal: sinon.stub(),
    };
    const fakeCookieStorage: any = {
        getVal: sinon.stub(),
        setVal: sinon.stub(),
    };

    beforeEach(() => {
        fakeCookieStorage.getVal.returns('');
        sandbox
            .stub(globalStorage, 'getGlobalStorage')
            .returns(fakeGlobalStorage);
        sandbox.stub(cookie, 'globalCookieStorage').returns(fakeCookieStorage);
        checkCookieStub = sandbox.stub(cookie, 'checkCookie').returns(true);
        sandbox.stub(gdprCookie, 'isCookieAllowed').returns(true);
    });

    afterEach(() => {
        sandbox.restore();
        fakeCookieStorage.getVal.resetHistory();
        fakeCookieStorage.setVal.resetHistory();
    });

    it("Sets color from cookie if it's set", () => {
        const ctx: any = {
            isFinite: () => true,
        };
        const counterSettings: any = {};
        fakeCookieStorage.getVal.returns('w');

        const isWhite = isVisitColorWhite(ctx, counterSettings);
        sinon.assert.calledWith(
            fakeCookieStorage.getVal,
            VISIT_COLOR_COOKIE_NAME,
        );
        chai.assert(isWhite);
        fakeCookieStorage.setVal.calledWith(VISIT_COLOR_COOKIE_NAME, 'w');

        fakeCookieStorage.getVal.returns('b');
        const isBlack = !isVisitColorWhite(ctx, counterSettings);
        chai.assert(isBlack);
        fakeCookieStorage.setVal.calledWith(VISIT_COLOR_COOKIE_NAME, 'b');
    });

    it('Disables wisor if metrika is turned off or in opera mini', () => {
        const ctx: any = {
            isFinite: () => true,
            navigator: {
                userAgent: 'opera mini',
            },
        };
        const counterSettings: any = {};

        chai.assert(!isVisitColorWhite(ctx, counterSettings), 'opera mini');
        fakeCookieStorage.setVal.calledWith(VISIT_COLOR_COOKIE_NAME, 'b');

        checkCookieStub.returns(false);
        ctx.navigator.userAgent = 'some ua';
        chai.assert(
            !isVisitColorWhite(ctx, counterSettings),
            'disabled by cookie',
        );
        fakeCookieStorage.setVal.calledWith(VISIT_COLOR_COOKIE_NAME, 'b');
    });

    it('Sets color according with sampling shares', () => {
        const ctx: any = { isFinite: () => true };
        const counterSettings: any = {
            settings: {
                webvisor: {
                    recp: 2,
                },
            },
        };

        chai.assert(isVisitColorWhite(ctx, counterSettings), 'recp > 1');

        counterSettings.settings.webvisor.recp = 0.5;
        fakeGlobalStorage.getVal.returns(1);
        chai.assert(isVisitColorWhite(ctx, counterSettings), 'in sampling');
        fakeGlobalStorage.getVal.calledWith('hitId');

        fakeGlobalStorage.getVal.returns(10000 * 0.5 + 1);
        chai.assert(
            !isVisitColorWhite(ctx, counterSettings),
            'outside of sampling',
        );
    });
});
