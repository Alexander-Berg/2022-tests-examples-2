import * as sinon from 'sinon';
import * as crossDomain from '@src/middleware/crossDomain/utils';
import * as fingerPrint from '@src/providers/fingerPrint';
import * as localStorage from '@src/storage/localStorage';
import * as browser from '@src/utils/browser';
import { FIP_KEY } from '../const';

describe('providers / fingerPrint', () => {
    const sandbox = sinon.createSandbox();
    const windowStub = {
        navigator: {
            language: 'ru',
        },
        screen: {
            width: 800,
            height: 600,
        },
    } as any;

    let localStorageStub: sinon.SinonStub<any, any>;
    let isFFStub: sinon.SinonStub<any, any>;
    let isITPDisabledStub: sinon.SinonStub<any, any>;

    const localStore = {
        getVal: () => null,
        setVal: sandbox.stub(),
    };

    beforeEach(() => {
        isFFStub = sandbox.stub(browser, 'isFF');
        isITPDisabledStub = sandbox.stub(crossDomain, 'isITPDisabled');
        localStorageStub = sandbox
            .stub(localStorage, 'globalLocalStorage')
            .returns(localStore as any);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('should work correct with correct bbrowser and factors', () => {
        isITPDisabledStub.returns(false);
        isFFStub.returns(true);
        const expectation = [
            '08cddc828a0a4cecdead9052886a5778',
            '0e838d949e6c90dce381b16c12d74379',
        ].join('-');
        fingerPrint.fingerPrint(windowStub, [() => '1', () => '2']);
        sinon.assert.calledWith(localStore.setVal, FIP_KEY, expectation);
    });

    it('should not launch if first check fails', () => {
        isITPDisabledStub.returns(true);
        isFFStub.returns(false);
        fingerPrint.fingerPrint(windowStub, [() => '1', () => '2']);
        sinon.assert.notCalled(localStorageStub);
    });
});
