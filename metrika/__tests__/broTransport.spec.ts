import * as chai from 'chai';
import sinon, { createSandbox } from 'sinon';
import * as errorLogger from '@src/utils/errorLogger';
import * as fetchTransport from '@src/transport/fetch';
import { CONTENT_TYPE_HEADER } from '@src/sender/default/const';
import { TransportOptions } from '@src/transport/types';
import { TELEMETRY_QUERY_KEY } from '@src/utils/telemetry/const';
import { useBroTransport } from '../broTransport';
import { TRANSPORT_NAME, FETCH_TRANSPORT_ID } from '../const';
import { Navigator } from '../types';

describe('bro transport', () => {
    const testUrl = 'https://smth.com';
    const testBody = 'hello beacon';
    const isGDPRStub = Math.random() > 0.49;
    const expectedDefaultAnswer = {
        settings: {
            pcs: '1',
            webvisor: {
                ['arch_type']: 'html',
                date: '2019-11-07 13:34:37',
                forms: 1,
                recp: '0.00000',
                urls: 'regexp:.*',
            },
            eu: +isGDPRStub,
        },
        userData: {},
    };
    const sandbox = createSandbox();
    let namespace: Navigator;
    let ctxStub: any;
    let fetchStub: sinon.SinonStub;
    let onlineTransportStub: sinon.SinonStub;
    let sendBeaconStub: sinon.SinonStub;
    type CtxSettings = Partial<{
        isGDPR: boolean;
        method: any;
        onLine: boolean;
    }>;
    const createCtx = ({
        isGDPR = isGDPRStub,
        method = sendBeaconStub,
        onLine = true,
    }: CtxSettings = {}): any => {
        namespace = {
            [TRANSPORT_NAME]: method,
        };
        return {
            yandex: {
                private: {
                    user: {
                        getRegion: () => Promise.resolve({ isGDPR }),
                    },
                },
                experimental: {
                    navigator: namespace,
                },
            },
            navigator: {
                onLine,
            },
        };
    };

    beforeEach(() => {
        sendBeaconStub = sandbox.stub();
        onlineTransportStub = sandbox.stub().returns(Promise.resolve());
        ctxStub = createCtx();
        sandbox
            .stub(errorLogger, 'errorLogger')
            .callsFake((ctx, scopeName, fn) => {
                return (...args) => {
                    if (fn) {
                        fn(...args);
                    }
                };
            });
        fetchStub = sandbox
            .stub(fetchTransport, 'useFetch')
            .returns(onlineTransportStub);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('should call yandex beacon API', () => {
        const transport = useBroTransport(ctxStub) as any;
        transport(testUrl, {});

        ctxStub.navigator.onLine = false;
        transport(testUrl, { rBody: testBody });

        const [firstUrl, firstBody] = sendBeaconStub.firstCall.args;
        const [secondUrl, secondBody] = sendBeaconStub.secondCall.args;

        chai.expect(firstUrl).to.eq(testUrl);
        chai.expect(firstBody).to.eq('');
        chai.expect(secondUrl).to.eq(testUrl);
        chai.expect(secondBody).to.eq(testBody);

        sinon.assert.calledTwice(sendBeaconStub);
        sinon.assert.calledOn(sendBeaconStub.firstCall, namespace);
        sinon.assert.calledOn(sendBeaconStub.secondCall, namespace);

        sinon.assert.notCalled(onlineTransportStub);
    });

    it('options request: should give default answer if offline', () => {
        const transport = useBroTransport(
            createCtx({
                onLine: false,
                method: sendBeaconStub,
            }) as any,
        ) as any;

        return transport(testUrl, { wmode: true }).then(
            (defaultAnswer: any) => {
                chai.expect(defaultAnswer).to.deep.eq(expectedDefaultAnswer);
                sinon.assert.notCalled(onlineTransportStub);
            },
        );
    });

    it('options request: should try an available transport if online', () => {
        const transport = useBroTransport(ctxStub) as any;
        const opt = { wmode: true };

        transport(testUrl, opt);

        const [actualUrl, actualOptions] = onlineTransportStub.firstCall.args;

        chai.expect(actualUrl).to.eq(testUrl);
        chai.expect(actualOptions).to.eq(opt);

        sinon.assert.calledOnce(onlineTransportStub);
    });

    it('options request: should fallback to default answer if available transport fails', () => {
        onlineTransportStub.returns(Promise.reject());
        const transport = useBroTransport(ctxStub) as any;

        return transport(testUrl, { wmode: true }).then((data: any) => {
            chai.expect(data).to.deep.eq(expectedDefaultAnswer);
        });
    });

    it('options request: should fallback to default answer if transport doesnt exist', () => {
        fetchStub.returns(false);
        const transport = useBroTransport(ctxStub) as any;

        return transport(testUrl, { wmode: true }).then(
            (defaultAnswer: any) => {
                chai.expect(defaultAnswer).to.deep.eq(expectedDefaultAnswer);
            },
        );
    });

    it('should pass content-type to API', () => {
        const contentType = 'poop';
        const transport = useBroTransport(ctxStub) as any;

        transport(testUrl, {
            rHeaders: { [CONTENT_TYPE_HEADER]: contentType },
        });

        const [actualUrl, actualBody, actualType] =
            sendBeaconStub.firstCall.args;

        chai.expect(actualUrl).to.eq(testUrl);
        chai.expect(actualBody).to.eq('');
        chai.expect(actualType).to.eq(contentType);

        sinon.assert.calledOnce(sendBeaconStub);
    });

    it('should call fetch if sendPersistentBeacon is missing', () => {
        const noBeaconCtx = createCtx({ method: null });
        const transport = useBroTransport(noBeaconCtx) as any;
        const opt = {};

        transport(testUrl, opt);

        sinon.assert.calledOnce(onlineTransportStub);

        const [actualUrl, actualOptions] = onlineTransportStub.getCall(0).args;

        chai.expect(actualUrl).to.eq(testUrl);
        chai.expect(actualOptions).to.eq(opt);
    });

    it('replaces telemetry "ti" flag if fetch is used', () => {
        const noBeaconCtx = createCtx({ method: null });
        const transport = useBroTransport(noBeaconCtx) as any;
        const opt: Partial<TransportOptions> = {
            rQuery: {
                [TELEMETRY_QUERY_KEY]: 'ti(123)',
            },
        };

        transport(testUrl, opt);
        const [actualUrl, actualOptions] = onlineTransportStub.getCall(0).args;

        chai.expect(actualUrl).to.equal(testUrl);
        chai.expect(actualOptions).to.deep.equal({
            rQuery: {
                t: `ti(${FETCH_TRANSPORT_ID})`,
            },
        });
    });
});
