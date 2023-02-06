import * as chai from 'chai';
import * as sinon from 'sinon';
import * as loc from '@src/utils/location';
import * as Browser from '@src/utils/browser';
import { HTTPS_PROTOCOL } from '@src/utils/browser/applePay';
import { applePayFactor } from '../applePay';

describe('Antiford applePayFactor', () => {
    const sandbox = sinon.createSandbox();
    let commonWindowStub: Window;
    let locationStub: sinon.SinonStub<any, any>;
    let isIframeStub: sinon.SinonStub<any, any>;

    beforeEach(() => {
        locationStub = sandbox.stub(loc, 'getLocation');
        locationStub.returns({ protocol: HTTPS_PROTOCOL } as any);
        isIframeStub = sandbox.stub(Browser, 'isIframe');
        isIframeStub.returns(false);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('applePay partly included', () => {
        commonWindowStub = {
            ApplePaySession: {
                canMakePayments: () => true,
            },
        } as any;
        const result = applePayFactor(commonWindowStub);
        chai.expect(result).to.be.equal(true);
    });

    it('applePay included', () => {
        commonWindowStub = {
            ApplePaySession: {
                supportsVersion: (n: number) => n === 8,
                canMakePayments: () => true,
            },
        } as any;
        const result = applePayFactor(commonWindowStub);
        chai.expect(result).to.be.equal('8true');
    });

    it('applePay not included', () => {
        commonWindowStub = {
            ApplePaySession: null,
        } as any;
        const result = applePayFactor(commonWindowStub);
        chai.expect(result).to.be.equal('');
    });
});
