import * as chai from 'chai';
import * as sinon from 'sinon';
import * as loc from '@src/utils/location';
import * as Browser from '@src/utils/browser';
import { HTTPS_PROTOCOL, getAppleSDK } from '@src/utils/browser/applePay';

describe('applePay', () => {
    const sandbox = sinon.createSandbox();
    let commonWindowStub: Window;
    let locationStub: sinon.SinonStub<any, any>;
    let isIframeStub: sinon.SinonStub<any, any>;
    const AppleSDK = 'AppleSDK';

    beforeEach(() => {
        locationStub = sandbox.stub(loc, 'getLocation');
        locationStub.returns({ protocol: HTTPS_PROTOCOL });
        isIframeStub = sandbox.stub(Browser, 'isIframe');
        isIframeStub.returns(false);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('no ApplePaySession', () => {
        commonWindowStub = {} as any;
        const result = getAppleSDK(commonWindowStub);
        chai.expect(result).to.be.equal('');
    });

    it('in iframe', () => {
        isIframeStub.returns(true);
        commonWindowStub = {
            ApplePaySession: {
                canMakePayments: () => true,
            },
        } as any;
        const result = getAppleSDK(commonWindowStub);
        chai.expect(result).to.be.equal('');
    });

    it('with http', () => {
        locationStub.returns({ protocol: 'http:' });
        commonWindowStub = {
            ApplePaySession: {
                canMakePayments: () => true,
            },
        } as any;
        const result = getAppleSDK(commonWindowStub);
        chai.expect(result).to.be.equal('');
    });

    it('with ApplePaySession', () => {
        commonWindowStub = {
            ApplePaySession: {
                canMakePayments: () => AppleSDK,
            },
        } as any;
        const result = getAppleSDK(commonWindowStub);
        chai.expect(result).to.be.equal(AppleSDK);
    });
});
