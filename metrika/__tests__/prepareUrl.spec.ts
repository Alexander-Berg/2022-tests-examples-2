import * as chai from 'chai';
import * as sinon from 'sinon';
import * as loc from '@src/utils/location';
import { browserInfo } from '@src/utils/browserInfo';
import { ARTIFICIAL_BR_KEY } from '@src/providers/artificialHit/type';
import { EXPERIMENT_URL_PARAM } from '@src/providers/experiments/const';
import { WATCH_URL_PARAM, WATCH_REFERER_PARAM } from '@src/sender/watch';
import { SenderInfo } from '@src/sender/SenderInfo';
import { PAGE_VIEW_BR_KEY } from '@src/providers/hit/const';
import { DEFAULT_COUNTER_TYPE } from '@src/providers/counterOptions';
import { CounterOptions } from '@src/utils/counterOptions';
import { prepareUrlMiddleware, prepare } from '../prepareUrl';

describe('prepare url', () => {
    let prevCounterId = 123;
    const getCounterOptions = (): CounterOptions => {
        prevCounterId += 1;
        return {
            counterType: DEFAULT_COUNTER_TYPE,
            id: prevCounterId,
        };
    };
    const win = () => {
        return {} as any as Window;
    };
    let locationStub: sinon.SinonStub<any, any>;
    let testHref: string;
    const testHost = 'tes.t';
    beforeEach(() => {
        testHref = `http://${testHost}`;
        locationStub = sinon.stub(loc, 'getLocation');
    });
    afterEach(() => {
        locationStub.restore();
    });

    it('prepare root', () => {
        const winInfo = win();
        testHref = `http://${testHost}/fom/to`;
        locationStub.returns({
            href: `${testHref}`,
            host: testHost,
        });
        const testUrlPeace = 'main.domain/info';
        let result = prepare(winInfo, testUrlPeace);
        sinon.assert.calledOnce(locationStub);
        chai.expect(result).to.be.equal(
            `${testHref.split('/').slice(0, -1).join('/')}/${testUrlPeace}`,
        );
        result = prepare(winInfo, '/');

        chai.expect(result).to.be.equal(
            `${testHref.split('/').slice(0, -2).join('/')}/`,
        );
    });
    it('prepare absolute', () => {
        const winInfo = win();
        locationStub.returns({
            href: `${testHref}/fom/dfdf`,
            host: testHost,
        });
        const testUrlPeace = '/main.domain/info';
        const result = prepare(winInfo, testUrlPeace);
        sinon.assert.calledOnce(locationStub);
        chai.expect(result).to.be.equal(`${testHref}${testUrlPeace}`);
    });
    it('skip goals', () => {
        const winInfo = win();
        locationStub.returns({
            href: `${testHref}?g=1`,
            host: testHost,
        });
        const testUrlPeace = 'goal://main.domain/info';
        const result = prepare(winInfo, testUrlPeace);
        sinon.assert.calledOnce(locationStub);
        chai.expect(result).to.be.equal(testUrlPeace);
    });
    it('skip tel:', () => {
        const winInfo = win();
        locationStub.returns({
            href: `${testHref}?g=1`,
            host: testHost,
        });
        const testUrlPeace = 'tel:+79999999999';
        const result = prepare(winInfo, testUrlPeace);
        sinon.assert.calledOnce(locationStub);
        chai.expect(result).to.be.equal(testUrlPeace);
    });
    it('trim url and ref ', () => {
        const winInfo = win();
        locationStub.returns({
            href: `${testHref}?g=1`,
            host: testHost,
        });
        const testUrlPeace = `

           https://zen.yandex.ru

               `;
        const result = prepare(winInfo, testUrlPeace);
        chai.expect(result).to.be.equal('https://zen.yandex.ru');
    });
    it('prepare cgi', () => {
        const winInfo = win();
        locationStub.returns({
            href: `${testHref}?g=1`,
            host: testHost,
        });
        const testUrlPeace = '?test';
        const result = prepare(winInfo, testUrlPeace);
        sinon.assert.calledOnce(locationStub);
        chai.expect(result).to.be.equal(`${testHref}${testUrlPeace}`);
    });
    it('prepare hash', () => {
        const winInfo = win();
        locationStub.returns({
            href: testHref,
            host: testHost,
        });
        const testUrlPeace = '#test';
        let result = prepare(winInfo, testUrlPeace);
        sinon.assert.calledOnce(locationStub);
        chai.expect(result).to.be.equal(`${testHref}${testUrlPeace}`);
        const testHash = '#add';
        locationStub.returns({
            href: `${testHref}${testHash}`,
            host: testHost,
        });
        result = prepare(winInfo, testUrlPeace);
        chai.expect(result).to.be.equal(`${testHref}${testUrlPeace}`);
    });
    it('prepare referer', () => {
        const winInfo = win();
        locationStub.returns({
            href: testHref,
            host: testHost,
        });
        const middleware = prepareUrlMiddleware(
            winInfo,
            'h',
            getCounterOptions(),
        );
        if (!middleware.beforeRequest) {
            return;
        }
        const senderInfo: SenderInfo = {
            brInfo: browserInfo({
                [ARTIFICIAL_BR_KEY]: '1',
            }),
            urlParams: {
                [WATCH_REFERER_PARAM]: '',
            },
        };
        middleware.beforeRequest(senderInfo, () => {
            sinon.assert.calledOnce(locationStub);
            chai.expect(senderInfo.urlParams![WATCH_REFERER_PARAM]).to.be.equal(
                undefined,
            );
        });
    });
    it('prepare cgi url', () => {
        const winInfo = win();
        const testCgi = 'a=1';
        locationStub.returns({
            href: testHref,
            host: testHost,
        });
        const middleware = prepareUrlMiddleware(
            winInfo,
            'h',
            getCounterOptions(),
        );
        if (!middleware.beforeRequest) {
            return;
        }
        const senderInfo: SenderInfo = {
            brInfo: browserInfo({
                [ARTIFICIAL_BR_KEY]: '1',
            }),
            urlParams: {
                [WATCH_URL_PARAM]: `?${testCgi}`,
            },
        };
        middleware.beforeRequest(senderInfo, () => {
            sinon.assert.calledOnce(locationStub);
            chai.expect(senderInfo.urlParams![WATCH_URL_PARAM]).to.be.equal(
                `${testHref}?${testCgi}`,
            );
        });
    });
    it('prepare empty url', () => {
        const winInfo = win();
        locationStub.returns({
            href: testHref,
            host: testHost,
        });
        const middleware = prepareUrlMiddleware(
            winInfo,
            'h',
            getCounterOptions(),
        );
        if (!middleware.beforeRequest) {
            return;
        }
        const senderInfo: SenderInfo = {
            brInfo: browserInfo({
                [ARTIFICIAL_BR_KEY]: '1',
            }),
            urlParams: {},
        };
        middleware.beforeRequest(senderInfo, () => {
            sinon.assert.calledOnce(locationStub);
            chai.expect(senderInfo.urlParams![WATCH_URL_PARAM]).to.be.equal(
                testHref,
            );
        });
    });
    it('skips empty params', () => {
        const winInfo = win();
        const middleware = prepareUrlMiddleware(
            winInfo,
            'h',
            getCounterOptions(),
        );
        if (!middleware.beforeRequest) {
            return;
        }
        middleware.beforeRequest(
            {
                brInfo: browserInfo(),
            },
            () => {
                sinon.assert.notCalled(locationStub);
            },
        );
    });
    it('skips empty brInfo', () => {
        const winInfo = win();
        const middleware = prepareUrlMiddleware(
            winInfo,
            'h',
            getCounterOptions(),
        );
        if (!middleware.beforeRequest) {
            return;
        }
        middleware.beforeRequest({}, () => {
            sinon.assert.notCalled(locationStub);
        });
    });
    it(`sets experiment url param`, () => {
        const winInfo = win();
        const urlParams: Record<string, any> = {};
        const middleware = prepareUrlMiddleware(winInfo, 'h', {
            exp: '1',
            id: 123,
            counterType: '0',
        });
        locationStub.returns({
            href: `${testHref}`,
            host: testHost,
        });

        middleware.beforeRequest!(
            {
                urlParams,
                brInfo: browserInfo({ [PAGE_VIEW_BR_KEY]: '1' }),
            },
            () => {},
        );
        chai.expect(urlParams[EXPERIMENT_URL_PARAM], 'exp not set').to.be.equal(
            '1',
        );

        urlParams[EXPERIMENT_URL_PARAM] = null;
        middleware.beforeRequest!(
            {
                urlParams,
                brInfo: browserInfo({ [PAGE_VIEW_BR_KEY]: '1' }),
            },
            () => {},
        );
        chai.expect(
            urlParams[EXPERIMENT_URL_PARAM],
            "exp set but it does't expected",
        ).to.be.null;
    });
});
