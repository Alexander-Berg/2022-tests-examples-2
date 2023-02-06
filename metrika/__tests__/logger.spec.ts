import * as sinon from 'sinon';
import { config, host } from '@src/config';
import * as transportModule from '@src/transport';
import { argOptions } from '@inject';
import * as chai from 'chai';
import { ERROR_LOGGER_PROVIDER, LOGGER_PROVIDER } from '@src/providers';
import { log } from '@src/utils/logger';

describe('logger', () => {
    const sandbox = sinon.createSandbox();
    const locationHref = 'test';
    const ctxStub = {
        location: {
            href: locationHref,
        },
        JSON,
    } as any;
    const provider = ERROR_LOGGER_PROVIDER;
    const rBody = { test: 1 };
    const url = `${config.cProtocol}//${host}/watch/${config.ERROR_LOGGER_COUNTER}`;

    const transportStub = sandbox.stub().returns(Promise.resolve());

    let transportsListStub: sinon.SinonStub<any, any>;

    beforeEach(() => {
        transportsListStub = sandbox
            .stub(transportModule, 'getTransportList')
            .returns([[1, transportStub]]);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('calls getTransportList for transport', () => {
        transportsListStub.returns([]);

        log(ctxStub, rBody, LOGGER_PROVIDER);
        sinon.assert.calledOnce(transportsListStub);
        const { args } = transportsListStub.getCall(0);
        chai.expect(args[0]).to.eq(ctxStub);
        chai.expect(args[1]).to.eq(LOGGER_PROVIDER);
    });

    it('calls the transport provided by getTransportList', () => {
        log(ctxStub, rBody, provider);

        sinon.assert.calledOnce(transportStub);
        const { args } = transportStub.getCall(0);
        chai.expect(args[0]).to.eq(url);
        chai.expect(args[1].rQuery).to.deep.eq({
            ['browser-info']: `ar:1:pv:1:v:${config.buildVersion}:vf:${argOptions.version}`,
            ['page-url']: locationHref,
        });

        const parsedRequestBody = JSON.parse(
            decodeURIComponent(args[1].rBody.match(/site-info=(.*)$/)[1]),
        );
        chai.expect(parsedRequestBody).to.deep.equal(rBody);
    });
});
