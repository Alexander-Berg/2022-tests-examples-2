import * as sinon from 'sinon';
import * as counterUtils from '@src/utils/counter';
import * as domUtils from '@src/utils/dom';
import * as objectUtils from '@src/utils/object';
import * as firstPartyMethodUtils from '@src/providers/firstPartyMethod';
import { CounterObject } from '@src/utils/counter/type';
import { CounterOptions } from '@src/utils/counterOptions';
import { METHOD_NAME_PARAMS } from '@src/providers/params/const';
import { inputEventHandlerRaw } from '../inputEventHandler';
import { MAX_VAL_LENGTH } from '../const';

describe('providers / inputCollector', () => {
    const ctx = {} as Window;
    const counterOptions = {
        id: 123,
        counterType: '0',
    } as CounterOptions;
    const counterInstance = {} as CounterObject;
    const validPhone = '8(999)888-99-88';
    const validEmail = 'vasily-pupkin@yandex.ru';
    const inputEvent = (type?: string) => (value: string) =>
        ({
            target: { value, type },
        } as unknown as Event);
    const phoneInputEvent = inputEvent('tel');
    const emailInputEvent = inputEvent();

    const sandbox = sinon.createSandbox();
    let getCounterInstanceStub: sinon.SinonStub<
        [ctx: Window, counterOptions: CounterOptions],
        CounterObject | undefined
    >;
    let hashValStub: sinon.SinonStub<
        [ctx: Window, val: string],
        Promise<string>
    >;
    let getElementPathStub: sinon.SinonStub<
        [
            ctx: Window,
            el: HTMLElement | null,
            ignored?: HTMLElement | undefined,
        ],
        string
    >;
    let getPathSpy: sinon.SinonSpy<[ctx: any, path: string], any>;
    let paramsSpy: sinon.SinonSpy<[...a: any[]], CounterObject>;

    beforeEach(() => {
        getCounterInstanceStub = sandbox
            .stub(counterUtils, 'getCounterInstance')
            .returns(counterInstance);
        hashValStub = sandbox
            .stub(firstPartyMethodUtils, 'hashVal')
            .resolves('result');
        getElementPathStub = sandbox
            .stub(domUtils, 'getElementPath')
            .returns('path');

        getPathSpy = sandbox.spy(objectUtils, 'getPath');
        paramsSpy = sandbox.spy();
        counterInstance[METHOD_NAME_PARAMS] = paramsSpy;
    });

    afterEach(() => {
        sandbox.restore();
    });

    describe('inputEventHandler', () => {
        describe('does nothing for', () => {
            it('not found counter', () => {
                getCounterInstanceStub.returns(undefined);
                const event = phoneInputEvent(validPhone);
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.notCalled(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('events with no-type target', () => {
                const event = {} as Event;
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledOnce(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('events with no value', () => {
                const event = { target: {} } as Event;
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledTwice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('events with empty value', () => {
                const event = emailInputEvent('  ');
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledTwice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('events with too long value', () => {
                const event = emailInputEvent('8'.repeat(MAX_VAL_LENGTH));
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledTwice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('inputs not representing email or phone', () => {
                const event = emailInputEvent('simple input');
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledThrice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('phones with letters', () => {
                const event = phoneInputEvent(`${validPhone}z`);
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledThrice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('phones starting with non-digit and non-"+"', () => {
                const event = phoneInputEvent(`(${validPhone}`);
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledThrice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('phones starting with "+" followed by non-digit', () => {
                const event = phoneInputEvent(`+(${validPhone}`);
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledThrice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('phones ending with non-digit', () => {
                const event = phoneInputEvent(`${validPhone})`);
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledThrice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('too short phones', () => {
                const event = phoneInputEvent(validPhone.slice(0, -1));
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledThrice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('too long phones', () => {
                const event = phoneInputEvent(validPhone.repeat(2));
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledThrice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });

            it('too short emails', () => {
                const event = emailInputEvent('a@bc');
                inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledThrice(getPathSpy);
                sinon.assert.notCalled(hashValStub);
            });
        });

        describe('hashes and sends input value', () => {
            it('for a valid phone', async () => {
                const event = phoneInputEvent(validPhone);
                await inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledOnce(hashValStub);
                sinon.assert.calledOnceWithExactly(
                    getElementPathStub,
                    ctx,
                    event.target as HTMLElement,
                );
                sinon.assert.calledOnceWithExactly(paramsSpy, {
                    ['__ym']: {
                        [`fi`]: 'a(0)b(path)c(result)',
                    },
                });
            });

            it('for a valid email', async () => {
                const event = emailInputEvent(validEmail);
                await inputEventHandlerRaw(ctx, counterOptions, event);
                sinon.assert.calledOnce(hashValStub);
                sinon.assert.calledOnceWithExactly(
                    getElementPathStub,
                    ctx,
                    event.target as HTMLElement,
                );
                sinon.assert.calledOnceWithExactly(paramsSpy, {
                    ['__ym']: {
                        [`fi`]: 'a(1)b(path)c(result)',
                    },
                });
            });
        });
    });
});
