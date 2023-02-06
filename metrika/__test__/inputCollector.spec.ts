import * as sinon from 'sinon';
import * as counterSettings from '@src/utils/counterSettings';
import * as domUtils from '@src/utils/dom';
import * as eventUtils from '@src/utils/events';
import * as firstPartyMethodUtils from '@src/providers/firstPartyMethod';
import * as inputUtils from '@src/utils/webvisor/inputUtils';
import { CounterOptions } from '@src/utils/counterOptions';
import { inputCollector } from '..';

describe('providers / inputCollector', () => {
    const ctx = {
        document: { body: {} },
    } as unknown as Window;
    const counterOptions = {
        id: 123,
        counterType: '0',
    } as CounterOptions;
    const hitInfo = {
        settings: {
            cf: 1,
        },
        userData: {},
    } as unknown as counterSettings.CounterSettings;
    const eventSetterOnSpy = sinon.spy();
    const eventSetter: eventUtils.EventSetter = {
        on: eventSetterOnSpy,
        un: sinon.spy(),
    };
    const validInputs = [
        { type: 'text' },
        { type: 'email' },
    ] as unknown as NodeListOf<HTMLInputElement>;

    const sandbox = sinon.createSandbox();
    let isQuerySelectorSupportedStub: sinon.SinonStub<[ctx: Window], boolean>;
    let isEncoderSupportedStub: sinon.SinonStub<[ctx: Window], boolean>;
    let getCounterSettingsStub: sinon.SinonStub<
        [
            ctx: Window,
            counterOptions: CounterOptions,
            callBack: (opt: counterSettings.CounterSettings) => void,
        ],
        Promise<unknown>
    >;
    let cEventStub: sinon.SinonStub<[ctx: Window], eventUtils.EventSetter>;
    let querySelectorAllStub: sinon.SinonStub<
        [string],
        NodeListOf<HTMLInputElement>
    >;
    let isIgnoredStub: sinon.SinonStub<
        [ctx: Window, input: HTMLElement],
        boolean
    >;

    beforeEach(() => {
        hitInfo.settings.cf = 1;

        isQuerySelectorSupportedStub = sandbox
            .stub(domUtils, 'isQuerySelectorSupported')
            .returns(true);
        isEncoderSupportedStub = sandbox
            .stub(firstPartyMethodUtils, 'isEncoderSupported')
            .returns(true);
        getCounterSettingsStub = sandbox
            .stub(counterSettings, 'getCounterSettings')
            .callsFake((_, __, fn) => {
                return new Promise((resolve) => resolve(fn(hitInfo)));
            });
        cEventStub = sandbox.stub(eventUtils, 'cEvent').returns(eventSetter);
        querySelectorAllStub =
            sandbox.stub<[string], NodeListOf<HTMLInputElement>>();
        ctx.document.body.querySelectorAll = querySelectorAllStub;
        isIgnoredStub = sandbox.stub(inputUtils, 'isIgnored').returns(false);
    });

    afterEach(() => {
        sandbox.restore();
    });

    describe('does nothing if', () => {
        it('querySelector not supported', () => {
            isQuerySelectorSupportedStub.returns(false);
            inputCollector(ctx, counterOptions);
            sinon.assert.notCalled(getCounterSettingsStub);
        });

        it('encoder not supported', () => {
            isEncoderSupportedStub.returns(false);
            inputCollector(ctx, counterOptions);
            sinon.assert.notCalled(getCounterSettingsStub);
        });

        it('not enabled in counter settings', () => {
            hitInfo.settings.cf = 0;
            inputCollector(ctx, counterOptions);
            sinon.assert.calledOnce(getCounterSettingsStub);
            sinon.assert.notCalled(cEventStub);
        });

        it('no inputs found', () => {
            const inputs = [] as unknown as NodeListOf<HTMLInputElement>;
            querySelectorAllStub.returns(inputs);
            inputCollector(ctx, counterOptions);
            sinon.assert.calledOnce(getCounterSettingsStub);
            sinon.assert.calledOnce(cEventStub);
            sinon.assert.notCalled(eventSetterOnSpy);
        });

        it('found inputs are ignored', () => {
            querySelectorAllStub.returns(validInputs);
            isIgnoredStub.returns(true);
            inputCollector(ctx, counterOptions);
            sinon.assert.calledOnce(getCounterSettingsStub);
            sinon.assert.calledOnce(cEventStub);
            sinon.assert.notCalled(eventSetterOnSpy);
        });

        it('found inputs are not in allowed types', () => {
            const inputs = [
                { type: 'checkbox' },
            ] as unknown as NodeListOf<HTMLInputElement>;
            querySelectorAllStub.returns(inputs);
            inputCollector(ctx, counterOptions);
            sinon.assert.calledOnce(getCounterSettingsStub);
            sinon.assert.calledOnce(cEventStub);
            sinon.assert.notCalled(eventSetterOnSpy);
        });

        it('found inputs have autocomplete within restricted range', () => {
            const inputs = [
                { type: 'email', autocomplete: 'name' },
                { type: 'email', autocomplete: 'shipping' },
                { type: 'email', autocomplete: 'cc-number' },
            ] as unknown as NodeListOf<HTMLInputElement>;
            querySelectorAllStub.returns(inputs);
            inputCollector(ctx, counterOptions);
            sinon.assert.calledOnce(getCounterSettingsStub);
            sinon.assert.calledOnce(cEventStub);
            sinon.assert.notCalled(eventSetterOnSpy);
        });
    });

    describe('for valid inputs', () => {
        it('subscribes to "blur" event of each input', () => {
            querySelectorAllStub.returns(validInputs);

            inputCollector(ctx, counterOptions);

            sinon.assert.calledOnce(getCounterSettingsStub);
            sinon.assert.calledOnce(cEventStub);
            sinon.assert.calledTwice(eventSetterOnSpy);
            eventSetterOnSpy
                .getCalls()
                .forEach((call, index) =>
                    sinon.assert.calledWithExactly(
                        call,
                        validInputs[index],
                        ['blur'],
                        sinon.match.any,
                    ),
                );
        });
    });
});
