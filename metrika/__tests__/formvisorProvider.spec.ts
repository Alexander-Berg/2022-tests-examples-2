import * as chai from 'chai';
import * as sinon from 'sinon';
import * as flags from '@src/inject';
import * as debug from '@src/providers/debugger/dispatchEvent';
import * as domUtils from '@src/utils/dom';
import * as sender from '@src/sender';
import * as serializer from '@private/src/buffer/serializer/FormvisorSerializer';
import * as visorbuffer from '@private/src/buffer/VisorBuffer';
import * as globalStorage from '@src/storage/global';
import * as events from '@src/utils/events';
import * as arrayUtils from '@src/utils/array';
import * as optoutProvider from '@src/providers/optout';
import * as cookie from '@src/storage/cookie';
import * as gdprCookie from '@src/middleware/gdpr/cookie';
import { IS_EU_CONFIG_KEY } from '@src/middleware/counterFirstHit';
import * as settings from '@src/utils/counterSettings';
import { AbstractBufferInterface } from '@private/src/buffer/AbstractBuffer';
import { SUPER_DEBUG_FEATURE } from '@generated/features';
import { CounterOptions } from '@src/utils/counterOptions';
import * as getIsRsyaCounterVal from '@private/src/providers/formvisor/getIsRsyaCounterVal';
import { useWebvisorProviderRaw } from '../../webvisor/webvisor';
import {
    eventsWithForceFlushFormvisor,
    getTransformersMapFormvisor,
} from '../transformersMap';
import { useFormvisorProviderRaw } from '../formvisorProvider';
import * as formvisor from '../formvisor';

// Здесь тестируем сам провайдер (useProvider тестируется ниже)
describe('formvisor provider', () => {
    let win: Window;
    const sandbox = sinon.createSandbox();
    let cEvent: sinon.SinonStub;
    let eventHandlerOn: sinon.SinonStub;
    let eventHandlerUn: sinon.SinonStub;
    let eventHandlerUnsubscribe: sinon.SinonStub;
    let buffer: AbstractBufferInterface<Event, number[]>;
    let bufferPush: sinon.SinonStub;

    beforeEach(() => {
        sandbox.stub(debug, 'dispatchDebuggerEvent');
        win = {
            document: {
                addEventListener: () => {},
            },
        } as any as Window;

        // Buffer
        bufferPush = sandbox.stub();
        buffer = {
            push: bufferPush,
            flush: () => {},
        } as any as AbstractBufferInterface<Event, number[]>;

        // Events
        eventHandlerUnsubscribe = sandbox.stub();
        eventHandlerOn = sandbox.stub().returns(eventHandlerUnsubscribe);
        eventHandlerUn = sandbox.stub();

        cEvent = sandbox.stub(events, 'cEvent').returns({
            on: eventHandlerOn,
            un: eventHandlerUn,
        });
        sandbox
            .stub(arrayUtils, 'cIndexOf')
            .returns((needle: any, haystack: any[]) =>
                haystack.indexOf(needle),
            );

        sandbox.stub(domUtils, 'querySelectorByTagName').returns([]);
        sandbox.stub(domUtils, 'getBody').returns({} as HTMLBodyElement);
        sandbox.stub(gdprCookie, 'isCookieAllowed').returns(true);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('should create provider, start, handle event witch trow exeption', () => {
        const event = Object.create(
            {},
            {
                type: {
                    get: () => {
                        throw new Error('Bad type');
                    },
                },
            },
        ) as any as Event;

        const provider = formvisor.formvisorProvider(
            win,
            buffer,
            getTransformersMapFormvisor,
            eventsWithForceFlushFormvisor,
        );

        provider.start();

        const firstHandlerOn = eventHandlerOn.getCall(0);
        if (firstHandlerOn) {
            // Провайдер работает: кинем ивент в подписку
            firstHandlerOn.args[2](event);
        }

        provider.stop();

        sinon.assert.called(cEvent);

        const onCalls = eventHandlerOn.getCalls().length;
        const unCalls = eventHandlerOn.getCalls().length;

        chai.expect(onCalls).to.be.greaterThan(1);
        chai.expect(unCalls).to.be.greaterThan(1);
        chai.expect(onCalls).to.be.equal(unCalls);

        sinon.assert.notCalled(bufferPush);
    });
    it('should create provider, start, handle event and then stop', () => {
        // Событие, которое провайдер должен поймать
        const event = {
            type: 'click',
        } as any as Event;

        const provider = formvisor.formvisorProvider(
            win,
            buffer,
            getTransformersMapFormvisor,
            eventsWithForceFlushFormvisor,
        );

        provider.start();

        const firstHandlerOn = eventHandlerOn.getCall(0);
        if (firstHandlerOn) {
            // Провайдер работает: кинем ивент в подписку
            firstHandlerOn.args[2](event);
        }

        provider.stop();

        sinon.assert.called(cEvent);

        const onCalls = eventHandlerOn.getCalls().length;
        const unCalls = eventHandlerOn.getCalls().length;

        chai.expect(onCalls).to.be.greaterThan(1);
        chai.expect(unCalls).to.be.greaterThan(1);
        chai.expect(onCalls).to.be.equal(unCalls);

        sinon.assert.calledWith(bufferPush, event);
    });
});

// Здесь тестируем useProvider (провайдер тестируется выше)
describe('useformvisor provider', () => {
    let win: Window;
    let getSenderStub: sinon.SinonStub;
    let startSpy: sinon.SinonSpy;
    let stopSpy: sinon.SinonSpy;
    let setGlobalValSpy: sinon.SinonSpy;
    let FormvisorSerializerStub: sinon.SinonStub;
    let VisorBufferStub: sinon.SinonStub;
    const sandbox = sinon.createSandbox();
    const counterOpt: CounterOptions = {
        webvisor: true,
        id: Math.random() * 100,
        counterType: '0',
    };

    beforeEach(() => {
        sandbox.stub(getIsRsyaCounterVal, 'getIsRsyaCounterVal').returns(false);
        win = {
            document: {
                addEventListener: () => {},
            },
            isFinite: () => true,
        } as any as Window;
        sandbox.stub(debug, 'dispatchDebuggerEvent');

        // Сам провайдер не запускается
        // Он тестируется в блоке describe выше
        startSpy = sandbox.spy();
        stopSpy = sandbox.spy();
        sandbox.stub(formvisor, 'formvisorProvider').returns({
            start: startSpy,
            stop: stopSpy,
        });
        sandbox.stub(flags, 'flags').value({
            [SUPER_DEBUG_FEATURE]: false,
        });

        // Serializer
        FormvisorSerializerStub = sandbox.stub(
            serializer,
            'FormvisorSerializer',
        );

        // Buffer
        VisorBufferStub = sandbox.stub(visorbuffer, 'VisorBuffer');

        // Sender
        getSenderStub = sandbox.stub(sender, 'getSender');

        // Global Storage
        setGlobalValSpy = sinon.spy();
        sandbox.stub(globalStorage, 'getGlobalStorage').returns({
            setVal: setGlobalValSpy,
            getVal: sinon.stub(),
        } as any);

        sandbox.stub(cookie, 'globalCookieStorage').returns({
            getVal: sinon.stub().returns('w'),
            setVal: sinon.stub(),
        } as any);

        sandbox.stub(optoutProvider, 'isOptoutEnabled').returns(false);

        sandbox.stub(domUtils, 'querySelectorByTagName').returns([]);
        sandbox.stub(gdprCookie, 'isCookieAllowed').returns(true);
    });

    afterEach(() => {
        sandbox.restore();
    });

    const checkStart = () => {
        sinon.assert.called(getSenderStub);
        sinon.assert.calledWith(FormvisorSerializerStub, win);
        sinon.assert.calledWith(VisorBufferStub, win);
        sinon.assert.called(startSpy);
        sinon.assert.notCalled(stopSpy);
    };

    const stubSettingsStorage = (isEU: boolean) => {
        sandbox.stub(settings, 'getCounterSettings').callsFake((_, _1, fn) => {
            return new Promise((resolve) => {
                return resolve(
                    fn({
                        settings: { pcs: '', eu: isEU },
                        userData: {},
                    } as any),
                );
            });
        });
    };

    it("shouldn't start if disableFomAnalytics is true", () => {
        return useFormvisorProviderRaw(win, {
            disableFomAnalytics: true,
        } as any).then(() => {
            sinon.assert.notCalled(FormvisorSerializerStub);
            sinon.assert.notCalled(getSenderStub);
        });
    });

    it('should start useFormvisorProvider', () => {
        stubSettingsStorage(false);
        useFormvisorProviderRaw(win, counterOpt);
        checkStart();
    });

    // Это тестирования webvisor, который находится в другой директории
    // Не хочется дублировать код для его тестов, поэтому тестируем здесь
    it('should start useWebvisorProviderRaw', () => {
        stubSettingsStorage(false);
        useWebvisorProviderRaw(win, counterOpt);
        checkStart();
    });

    it('should start with isEU false in global storage', () => {
        stubSettingsStorage(false);
        useFormvisorProviderRaw(win, counterOpt);
        sinon.assert.calledWith(setGlobalValSpy, IS_EU_CONFIG_KEY, false);
    });

    it('should start with isEU true in global storage', () => {
        stubSettingsStorage(true);
        useFormvisorProviderRaw(win, counterOpt);
        sinon.assert.calledWith(setGlobalValSpy, IS_EU_CONFIG_KEY, true);
    });
});
