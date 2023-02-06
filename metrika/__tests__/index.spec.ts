import * as chai from 'chai';
import * as sinon from 'sinon';
import * as debug from '@src/providers/debugger/dispatchEvent';
import * as flags from '@src/inject';
import * as globalStorage from '@src/storage/global';
import * as settings from '@src/utils/counterSettings';
import * as functionUtils from '@src/utils/function';
import * as br from '@src/utils/browser';
import * as events from '@src/utils/events';
import * as asyncUtils from '@src/utils/async';
import * as defer from '@src/utils/defer';
import * as serializer from '@private/src/buffer/serializer/JSONBufferSerializer';
import {
    Visor2Buffer,
    BUFFER_NAME_EVENTS,
    BUFFER_NAME_MUTATIONS,
    AGGREGATE_EVENT_KEY,
    PUSH_DATA_EVENT_KEY,
    SENDER_ERROR_EVENT_KEY,
} from '@private/src/buffer/Visor2Buffer';
import * as dConsole from '@src/providers/debugConsole';
import * as counterOptions from '@src/utils/counterOptions';
import * as waitForBody from '@src/utils/dom/waitForBody';
import { SUPER_DEBUG_FEATURE } from '@generated/features';
import * as pfs from '@private/src/buffer/serializer/ProtoBufferSerializer';
import {
    WV2_COUNTER_KEY,
    WV2_STOP_RECORDER_KEY,
    WV2_HIT_TIME_LIMIT,
} from '../const';
import { useWebvisor2Provider } from '../webvisor2';
import * as recorder from '../recorder/Recorder';
import * as activity from '../collectActivity';
import * as visitColor from '../visitColor';
import * as recorderOpts from '../getRecorderOptions';
import * as SB from '../Visor2SenderBuffer';

describe('webvisor2 provider', () => {
    const win = { MutationObserver: {} as any } as any;
    const counterKey = 'key';
    const euFromSettings = 1;
    const recorderOptions = {
        isEU: true,
        recordForms: true,
        trustedHosts: undefined,
    };

    let isNativeMutationObserver: boolean;
    let isNativeElement: boolean;
    let isVisitWhite: boolean;

    let setGlobalValSpy: sinon.SinonSpy;
    let recorderStartSpy: sinon.SinonSpy;
    let recorderStopSpy: sinon.SinonSpy;

    let fromCharCodeStub: sinon.SinonStub<any, any>;

    const fakeSerializer: any = {
        isEnabled: () => true,
    };
    const fakeEventsSenderFunction = sinon.stub().resolves();
    const fakeMutationsSenderFunction = sinon.stub().resolves();

    let getGlobalValStub: sinon.SinonStub;
    let recorderStub: sinon.SinonStub;
    let JSONBufferSerializerStub: sinon.SinonStub;
    let getCounterKeyStub: sinon.SinonStub;
    let setDeferStub: sinon.SinonStub;
    let createSFStub: sinon.SinonStub;

    const fakeEventWrapper = { on: sinon.stub() };
    let eventWrapperStub: sinon.SinonStub;

    let getBufferStub: sinon.SinonStub;
    const mutationsBuffer: any = {
        on: sinon.stub(),
        push: sinon.stub(),
        flush: sinon.stub(),
    };
    const eventsBuffer: any = {
        on: sinon.stub(),
        push: sinon.stub(),
        flush: sinon.stub(),
    };

    const actvityCallbacks = {
        aggregate: () => {},
        onEventPush: () => {},
    };
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const sandbox = sinon.createSandbox();
    const fakeConsole = {
        warn: sandbox.stub(),
    };
    let counterOpts: any;
    let settingPromise: any;
    beforeEach(() => {
        sandbox.stub(debug, 'dispatchDebuggerEvent');
        sandbox.stub(flags, 'flags').value({
            [SUPER_DEBUG_FEATURE]: false,
        });
        sandbox.stub(pfs, 'checkProtobuf').returns(true);
        counterOpts = {
            id: 123,
            webvisor: true,
        };
        createSFStub = sandbox.stub(SB, 'Visor2SenderBuffer').returns({
            mutationsSenderFunction: fakeMutationsSenderFunction,
            eventsSenderFunction: fakeEventsSenderFunction,
        });
        setDeferStub = sandbox.stub(defer, 'setDefer');
        fakeConsole.warn.resetHistory();
        sandbox.stub(dConsole, 'DebugConsole').returns(fakeConsole as any);
        fromCharCodeStub = sandbox.stub(br, 'isBrokenFromCharCode');
        fromCharCodeStub.returns(false);

        eventWrapperStub = sandbox
            .stub(events, 'cEvent')
            .returns(fakeEventWrapper as any);

        isNativeMutationObserver = true;
        isNativeElement = true;
        isVisitWhite = true;
        sandbox.stub(asyncUtils, 'runAsync').callsFake((ctx, cb) => cb());
        sandbox
            .stub(recorderOpts, 'getRecorderOptions')
            .returns(asyncUtils.taskOf(recorderOptions));

        setGlobalValSpy = sandbox.spy();
        recorderStartSpy = sandbox.spy();
        recorderStopSpy = sandbox.spy();

        getGlobalValStub = sandbox.stub();
        getGlobalValStub.withArgs(WV2_COUNTER_KEY).callsFake(() => false);

        sandbox.stub(globalStorage, 'getGlobalStorage').returns({
            setVal: setGlobalValSpy,
            getVal: getGlobalValStub,
        } as any);
        sandbox.stub(settings, 'getCounterSettings').callsFake((_, _1, fn) => {
            settingPromise = new Promise((resolve) => {
                return resolve(fn({ settings: { eu: euFromSettings } } as any));
            });
            return settingPromise;
        });
        recorderStub = sandbox.stub(recorder, 'Recorder').returns({
            start: recorderStartSpy,
            stop: recorderStopSpy,
        });
        sandbox
            .stub(activity, 'getCollectActivityCallbacks')
            .returns(actvityCallbacks as any);
        sandbox
            .stub(functionUtils, 'isNativeFunction')
            .callsFake((functionName: string) =>
                functionName === 'Element'
                    ? isNativeElement
                    : isNativeMutationObserver,
            );
        sandbox
            .stub(visitColor, 'isVisitColorWhite')
            .callsFake(() => isVisitWhite);
        JSONBufferSerializerStub = sandbox
            .stub(serializer, 'JSONBufferSerializer')
            .returns(fakeSerializer);
        sandbox
            .stub(waitForBody, 'waitForBodyTask')
            .returns(asyncUtils.taskOf());
        getBufferStub = sandbox.stub(Visor2Buffer, 'getBuffer').callsFake(((
            counterCode: string,
            bufferName: string,
        ) => {
            if (bufferName === BUFFER_NAME_EVENTS) {
                return eventsBuffer;
            }
            if (bufferName === BUFFER_NAME_MUTATIONS) {
                return mutationsBuffer;
            }

            return {} as any;
        }) as any);
        getCounterKeyStub = sandbox
            .stub(counterOptions, 'getCounterKey')
            .returns(counterKey);
    });

    afterEach(() => {
        fakeEventWrapper.on.resetHistory();
        fakeMutationsSenderFunction.resetHistory();
        fakeEventsSenderFunction.resetHistory();

        eventsBuffer.on.resetHistory();
        eventsBuffer.push.resetHistory();
        eventsBuffer.flush.resetHistory();

        mutationsBuffer.on.resetHistory();
        mutationsBuffer.push.resetHistory();
        mutationsBuffer.flush.resetHistory();

        sandbox.restore();
    });

    const checkStart = () => {
        sinon.assert.calledWith(eventWrapperStub, win);
        chai.expect(
            setGlobalValSpy.withArgs(WV2_COUNTER_KEY, counterKey).called,
        ).to.be.ok;
        chai.expect(setGlobalValSpy.withArgs(WV2_STOP_RECORDER_KEY).called).to
            .be.ok;
        chai.expect(JSONBufferSerializerStub.calledWith(win)).to.be.ok;
        chai.expect(getCounterKeyStub.calledWith(counterOpts)).to.be.ok;
        chai.assert(createSFStub.calledWith(win, counterOpts, true));
    };

    const checkBufferInstances = () => {
        let [key, buffer] = getBufferStub.getCall(0).args;
        chai.expect(key).equal(counterKey);
        chai.expect(buffer).to.equal('m');

        [key, buffer] = getBufferStub.getCall(1).args;
        chai.expect(key).equal(counterKey);
        chai.expect(buffer).to.equal('e');

        sinon.assert.calledWith(
            eventsBuffer.on,
            AGGREGATE_EVENT_KEY,
            actvityCallbacks.aggregate,
        );
        sinon.assert.calledWith(
            eventsBuffer.on,
            PUSH_DATA_EVENT_KEY,
            actvityCallbacks.onEventPush,
        );

        const [collectDataCallback] = recorderStartSpy.getCall(0).args;

        const event = {
            type: 'event',
        };
        const mutation = {
            type: 'mutation',
        };
        const eof = {
            type: 'event',
            data: {
                type: 'eof',
            },
        };

        collectDataCallback([event]);
        chai.assert(eventsBuffer.push.calledWith(event));
        chai.assert(eventsBuffer.flush.notCalled);

        collectDataCallback([mutation]);
        chai.assert(mutationsBuffer.push.calledWith(mutation));
        chai.assert(mutationsBuffer.flush.notCalled);

        collectDataCallback([eof]);
        chai.assert(eventsBuffer.push.calledWith(eof));
        chai.assert(eventsBuffer.flush.called);
        chai.assert(mutationsBuffer.push.calledWith(eof));
        chai.assert(mutationsBuffer.flush.called);
    };

    it('has isEU in globalConfig (localStorage)', () => {
        useWebvisor2Provider(win, counterOpts);
        return settingPromise.then(() => {
            checkStart();
            checkBufferInstances();
            chai.expect(recorderStub.getCall(0).args).to.be.deep.eq([
                win,
                recorderOptions,
            ]);
        });
    });
    it('check counter option', () => {
        counterOpts.webvisor = false;
        useWebvisor2Provider(win, counterOpts);
        return settingPromise.then(() => {
            sinon.assert.notCalled(recorderStub);
        });
    });

    it('resolve counter settings and stops by timeout', () => {
        useWebvisor2Provider(win, counterOpts);
        return settingPromise.then(() => {
            checkStart();
            checkBufferInstances();
            chai.expect(recorderStub.getCall(0).args).to.be.deep.eq([
                win,
                recorderOptions,
            ]);
            const [ctx, callback, time] = setDeferStub.getCall(0).args;
            chai.expect(ctx).to.equal(win);
            chai.expect(time).to.equal(WV2_HIT_TIME_LIMIT);
            callback();
            sinon.assert.called(recorderStopSpy);
        });
    });

    it('resolve counter settings and stops by event', () => {
        useWebvisor2Provider(win, counterOpts);
        return settingPromise.then(() => {
            checkStart();
            checkBufferInstances();
            chai.expect(recorderStub.getCall(0).args).to.be.deep.eq([
                win,
                recorderOptions,
            ]);
            const [ctx, event, callback] = fakeEventWrapper.on.getCall(0).args;
            chai.expect(ctx).to.equal(win);
            chai.expect(event).to.deep.equal(['beforeunload', 'unload']);
            callback();
            sinon.assert.called(recorderStopSpy);
        });
    });

    it('resolve counter settings and stops by page send error', () => {
        useWebvisor2Provider(win, counterOpts);
        return settingPromise.then(() => {
            checkStart();
            checkBufferInstances();
            chai.expect(recorderStub.getCall(0).args).to.be.deep.eq([
                win,
                recorderOptions,
            ]);
            const [eventKey, callback] = mutationsBuffer.on.getCall(0).args;
            chai.expect(eventKey).to.equal(SENDER_ERROR_EVENT_KEY);
            callback([{ type: 'mutation' }]);
            sinon.assert.notCalled(recorderStopSpy);
            callback([{ type: 'mutation' }, { type: 'page' }]);
            sinon.assert.called(recorderStopSpy);
        });
    });

    it('has no MutationObserver', () => {
        isNativeMutationObserver = false;

        useWebvisor2Provider({} as any, counterOpts);
        return settingPromise.then(() => {
            chai.assert(recorderStub.notCalled);
        });
    });

    it('has non native Element', () => {
        isNativeElement = false;
        useWebvisor2Provider({} as any, counterOpts);
        return settingPromise.then(() => {
            chai.assert(recorderStub.notCalled);
        });
    });

    it('has non-native mutation observer', () => {
        isNativeMutationObserver = false;
        useWebvisor2Provider(win, counterOpts);
        return settingPromise.then(() => {
            checkStart();
            checkBufferInstances();
            chai.assert(fakeConsole.warn.called);
        });
    });

    it('not white color', () => {
        isVisitWhite = false;

        useWebvisor2Provider(win, counterOpts);
        return settingPromise.then(() => {
            chai.expect(recorderStub.getCall(0).args).to.be.deep.eq([
                win,
                recorderOptions,
            ]);
            sinon.assert.calledOnce(recorderStopSpy);
        });
    });
});
