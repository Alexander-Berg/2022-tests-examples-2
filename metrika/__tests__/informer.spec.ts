import * as chai from 'chai';
import * as sinon from 'sinon';
import * as configModule from '@src/config';
import * as errorLoggerUtils from '@src/utils/errorLogger';
import * as functionUtils from '@src/utils/function';
import * as domUtils from '@src/utils/dom';
import * as eventUtils from '@src/utils/events';
import { createInformer, rawOnClick as onClick } from '@src/providers/informer';
import { INFORMER_PROPERTY_NAME } from '@src/providers/informer/const';
import { yandexNamespace } from '@src/storage/global';

describe('Informer', () => {
    const prefs = {
        i: {} as unknown as Element,
        id: 124,
        lang: 'en',
    };
    const expectedPrefs = {
        ...prefs,
        domain: 'metrika-informer.com',
    };
    let commonWindowStub: Window;

    const sandbox = sinon.createSandbox();
    beforeEach(() => {
        commonWindowStub = {
            document: {
                addEventListener: () => {},
            },
            [yandexNamespace]: {
                [configModule.config.constructorName]: {},
            },
        } as any;
        sandbox
            .stub(errorLoggerUtils, 'errorLogger')
            .callsFake((ctx, scopeName, fn) => fn as (...args: any[]) => any);

        sandbox
            .stub(functionUtils as any, 'bind') // as any потому что падает из-за рекурсионных типов
            .callsFake((callback: (...args: any[]) => any) => {
                return callback;
            });
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Sets the onClick Event Listener', (done) => {
        const errorMessage = 'addEventListener was called with wrong arguments';
        const windowStub = {
            document: {},
        } as any;
        const eventStub = sandbox.stub(eventUtils, 'cEvent').callsFake(((
            arg: Window,
        ) => {
            chai.expect(arg, errorMessage).to.equal(windowStub);
            return {
                on(
                    element: Element,
                    eventName: string,
                    callback: (...args: any[]) => any,
                ) {
                    chai.expect(element, errorMessage).to.equal(
                        windowStub.document,
                    );
                    chai.expect(eventName).to.deep.equal(['click']);
                    chai.expect(callback, errorMessage).to.equal(onClick);
                    done();
                },
            };
        }) as unknown as typeof eventUtils.cEvent);

        createInformer(windowStub);
        eventStub.restore();
    });

    it('Sets the _informer property on the Counter constructor', () => {
        const configConstructorName = 'ConfigConstructorName';
        const windowStub = {
            ...commonWindowStub,
            [yandexNamespace]: {
                [configConstructorName]: {},
            },
        } as unknown as Window;
        const configStub = sinon.stub(configModule, 'config').value({
            constructorName: configConstructorName,
        });

        const counterConstructor =
            windowStub[yandexNamespace]![configConstructorName];
        const fn = createInformer(windowStub);
        fn(prefs);

        chai.expect(counterConstructor[INFORMER_PROPERTY_NAME]).to.deep.equal(
            expectedPrefs,
        );

        const differentPrefs = { ...prefs, id: 333 };
        const differentExpectedPrefs = { ...expectedPrefs, id: 333 };

        fn(differentPrefs);

        chai.expect(counterConstructor[INFORMER_PROPERTY_NAME]).to.deep.equal(
            differentExpectedPrefs,
        );

        configStub.restore();
    });

    it('Loads informer script if called for the 1st time', () => {
        const loadScriptFake = sinon.spy();
        const loadScriptStub = sinon
            .stub(domUtils, 'loadScript')
            .callsFake(loadScriptFake);

        const wrongArgsMessage = 'loadScript was called with wrong arguments';
        const callCountErrorMessage = 'loadScript was called more than once';
        const fn = createInformer(commonWindowStub);

        fn(prefs);

        chai.expect(
            loadScriptFake.getCall(0).args[0],
            wrongArgsMessage,
        ).to.equal(commonWindowStub);
        chai.expect(
            loadScriptFake.getCall(0).args[1],
            wrongArgsMessage,
        ).to.deep.equal({
            src: 'http://metrika-informer.com/metrika/informer.js',
        });
        chai.expect(loadScriptFake.callCount, callCountErrorMessage).to.equal(
            1,
        );

        fn({ ...prefs, id: 444 });
        fn({ ...prefs, id: 1488 });

        chai.expect(loadScriptFake.callCount, callCountErrorMessage).to.equal(
            1,
        );

        loadScriptStub.restore();
    });
});
