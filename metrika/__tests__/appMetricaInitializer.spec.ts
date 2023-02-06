import * as sinon from 'sinon';
import * as browserUtils from '@src/utils/browser';
import { useAppMetricaInitializer } from '@src/providers/appMetricaInitializer';
import * as counterSettingsUtils from '@src/utils/counterSettings';
import { CounterOptions } from '@src/utils/counterOptions';
import * as deferUtils from '@src/utils/defer';

describe('appMetrikaInitializer.ts', () => {
    const sandbox = sinon.createSandbox();
    let isAndroidWebViewStub: sinon.SinonStub;
    let isSafariWebViewStub: sinon.SinonStub;
    let getCounterSettingsStub: sinon.SinonStub;
    let setDeferStub: sinon.SinonStub;

    const win = {} as Window;
    const counterId = 124456;
    const counterOptions = {
        id: counterId,
    } as CounterOptions;

    beforeEach(() => {
        isAndroidWebViewStub = sandbox.stub(browserUtils, 'isAndroidWebView');
        isSafariWebViewStub = sandbox.stub(browserUtils, 'isSafariWebView');
        getCounterSettingsStub = sandbox.stub(
            counterSettingsUtils,
            'getCounterSettings',
        );

        setDeferStub = sandbox.stub(deferUtils, 'setDefer');
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('skip not android/ios', () => {
        isAndroidWebViewStub.returns(false);
        isSafariWebViewStub.returns(false);

        return useAppMetricaInitializer(win, counterOptions).then(() => {
            sinon.assert.notCalled(getCounterSettingsStub);
        });
    });

    it('init after interface load', () => {
        const initSpy = sandbox.spy();
        const data = { a: 1, b: 2 };

        isAndroidWebViewStub.returns(true);
        isSafariWebViewStub.returns(false);
        const winWithInterface = {
            AppMetricaInitializer: {
                init: initSpy,
            },
            JSON,
        } as any as Window;

        getCounterSettingsStub.callsFake((_ctx, _counterOptions, cb) => {
            cb({ settings: { sbp: data } });
        });

        return useAppMetricaInitializer(winWithInterface, counterOptions).then(
            () => {
                sinon.assert.calledWith(
                    initSpy,
                    JSON.stringify(Object.assign({}, data, { c: counterId })),
                );
            },
        );
    });

    it('init before interface load', (done) => {
        const initSpy = sandbox.spy();
        const data = { a: 1, b: 2 };

        isAndroidWebViewStub.returns(true);
        isSafariWebViewStub.returns(false);
        const winWithInterface = {
            JSON,
        } as any as Window;

        getCounterSettingsStub.callsFake((_ctx, _counterOptions, cb) => {
            cb({ settings: { sbp: data } });
        });

        setDeferStub.callsFake((ctx, cb) => {
            (winWithInterface as any).AppMetricaInitializer = { init: initSpy };
            cb();
            sinon.assert.calledWith(
                initSpy,
                JSON.stringify(Object.assign({}, data, { c: counterId })),
            );
            done();
        });

        return useAppMetricaInitializer(winWithInterface, counterOptions);
    });
});
