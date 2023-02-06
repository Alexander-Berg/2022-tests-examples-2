import * as chai from 'chai';
import * as sinon from 'sinon';
import * as functionUtils from '@src/utils/function';
import { getBrowser } from '../Browser';

describe('Browser', () => {
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        sandbox
            .stub(functionUtils, 'memo')
            .callsFake(((_: any, callback: Function) => callback()) as any);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('gets scrolling element', () => {
        const defaultCtx: any = {
            document: {
                scrollingElement: {},
                // Это чтобы мы не пытались вставить зум и вьюпорт
                querySelector: () => ({}),
            },
        };
        let browser = getBrowser(defaultCtx);
        chai.expect(browser.getScrollingElement()).to.equal(
            defaultCtx.document.scrollingElement,
        );

        const css1Ctx: any = {
            document: {
                compatMode: 'CSS1',
                querySelector: () => ({}),
                documentElement: {
                    scrollHeight: 100,
                },
                body: {
                    scrollHeight: 50,
                },
            },
        };
        browser = getBrowser(css1Ctx);
        chai.expect(browser.getScrollingElement()).to.equal(
            css1Ctx.document.documentElement,
        );

        const notCss1Ctx: any = {
            document: {
                compatMode: '',
                querySelector: () => ({}),
                documentElement: {
                    scrollHeight: 100,
                },
                body: {
                    scrollHeight: 50,
                },
            },
        };
        browser = getBrowser(notCss1Ctx);
        chai.expect(browser.getScrollingElement()).to.equal(
            notCss1Ctx.document.body,
        );
    });

    it('gets orientation', () => {
        const ctx: any = {
            document: {
                querySelector: () => ({}),
            },
            screen: {
                mozOrientation: {
                    angle: 666,
                },
            },
        };
        const browser = getBrowser(ctx);
        chai.expect(browser.getOrientation()).to.equal(666);

        delete ctx.screen.mozOrientation;
        chai.expect(browser.getOrientation()).to.equal(0);
    });
});
