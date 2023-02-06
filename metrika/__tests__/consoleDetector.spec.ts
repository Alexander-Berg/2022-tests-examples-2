import * as chai from 'chai';
import * as sinon from 'sinon';
import * as browser from '@src/utils/browser';
import * as consoleUtils from '@src/utils/console';
import * as globalStorage from '@src/storage/localStorage';

import { consoleDetectorRaw, CONSOLE_TEST_KEY } from '../consoleDetector';

describe('consoleDetector', () => {
    const sandbox = sinon.createSandbox();
    const fakeConsole: any = {
        log: sinon.stub(),
    };
    const fakeGlobalStorage: any = {
        setVal: sinon.stub(),
        getVal: sinon.stub(),
    };
    let isAndroidStub: sinon.SinonStub;
    let isIosStub: sinon.SinonStub;

    beforeEach(() => {
        sandbox
            .stub(globalStorage, 'globalLocalStorage')
            .returns(fakeGlobalStorage);
        sandbox.stub(consoleUtils, 'getConsole').returns(fakeConsole);
        isAndroidStub = sandbox.stub(browser, 'isAndroid');
        isIosStub = sandbox.stub(browser, 'isIOS');
    });

    afterEach(() => {
        sandbox.restore();
        fakeConsole.log.resetHistory();
        fakeGlobalStorage.setVal.resetHistory();
        fakeGlobalStorage.getVal.resetHistory();
    });

    it('does nothing on non mobile device', () => {
        const ctx: any = { chrome: {} };

        isAndroidStub.returns(false);
        isIosStub.returns(false);
        consoleDetectorRaw(ctx, {} as any);
        sinon.assert.notCalled(fakeGlobalStorage.getVal);
        sinon.assert.notCalled(fakeGlobalStorage.setVal);
        sinon.assert.notCalled(fakeConsole.log);
    });

    it('does nothing if global storage flag is set', () => {
        const ctx: any = { chrome: {} };
        isAndroidStub.returns(true);
        fakeGlobalStorage.getVal.returns(false);
        consoleDetectorRaw(ctx, {} as any);

        sinon.assert.calledWith(fakeGlobalStorage.getVal, CONSOLE_TEST_KEY);
        sinon.assert.notCalled(fakeGlobalStorage.setVal);
        sinon.assert.notCalled(fakeConsole.log);
    });

    it('detects open console', () => {
        const ctx: any = { chrome: {} };
        fakeGlobalStorage.getVal.returns(undefined);
        isAndroidStub.returns(true);

        consoleDetectorRaw(ctx, {} as any);
        sinon.assert.calledWith(fakeGlobalStorage.getVal, CONSOLE_TEST_KEY);
        sinon.assert.calledWith(
            fakeGlobalStorage.setVal,
            CONSOLE_TEST_KEY,
            false,
        );

        const [format, color, logging] = fakeConsole.log.getCall(0).args;
        chai.expect(format).to.equal('%c%s');
        chai.expect(color).to.equal('color: inherit');
        chai.expect(typeof logging).to.equal('function');
        chai.expect(logging.toString()).to.equal(
            'Yandex.Metrika counter is initialized',
        );

        sinon.assert.calledWith(
            fakeGlobalStorage.setVal,
            CONSOLE_TEST_KEY,
            true,
        );
    });
});
