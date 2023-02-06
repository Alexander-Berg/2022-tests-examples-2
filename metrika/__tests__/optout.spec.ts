import * as chai from 'chai';
import * as sinon from 'sinon';
import * as optoutProvider from '@src/providers/optout';
import { CounterOptions } from '@src/utils/counterOptions';
import { optout } from '../optout';

describe('optout', () => {
    const ctx = {} as any as Window;
    const provider = 'h';
    const counterOpt: CounterOptions = {
        id: 26302566,
        counterType: '0',
    };

    let providerStub: any;
    let middleware: any;
    let nextStub: any;
    let optoutValue: any;

    beforeEach(() => {
        providerStub = sinon
            .stub(optoutProvider, 'isOptoutEnabled')
            .callsFake(() => optoutValue);
        middleware = optout(ctx, provider, counterOpt);
        nextStub = sinon.fake();
    });

    afterEach(() => {
        providerStub.restore();
    });

    it('should call next if optout disabled', () => {
        optoutValue = undefined;

        if (middleware.beforeRequest) {
            middleware.beforeRequest({}, nextStub);
            chai.expect(providerStub.called).to.be.ok;
            chai.expect(nextStub.called).to.be.ok;
        }
    });

    it('should not call next if optout enabled', () => {
        optoutValue = true;

        if (middleware.beforeRequest) {
            middleware.beforeRequest({}, nextStub);
            chai.expect(providerStub.called).to.be.ok;
            chai.expect(nextStub.called).to.be.not.ok;
        }
    });
});
