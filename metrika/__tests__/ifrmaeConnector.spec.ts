import * as chai from 'chai';
import * as sinon from 'sinon';
import * as eventsUtils from '@src/utils/events';
import * as browserUtils from '@src/utils/browser';
import * as defer from '@src/utils/defer';
import * as urlUtils from '@src/utils/url';
import { noop } from '@src/utils/function';
import { KNOWN_ERROR } from '@src/utils/errorLogger/consts';
import {
    getIframeConnector,
    CONNECTOR_INITED,
    SLAVE_INIT_FREQUENCY,
    SLAVE_REGISTRATION_TIMEOUT,
    SLAVE_REGISTER_EVENT_NAME,
    SLAVE_REGISTER_PARENT_RESPONSE_EVENT_NAME,
    SLAVE_DATA_EVENT_NAME,
} from '../IframeConnector';

describe('webvisor2/iframeConnector', () => {
    let setDeferStub: sinon.SinonStub<any, any>;
    let clearDeferStub: sinon.SinonStub<any, any>;
    let isIframeStub: sinon.SinonStub<any, any>;
    const fakeEmitter = {
        on: sinon.stub(),
        off: sinon.stub(),
        trigger: sinon.stub(),
    } as any;
    const wrapperOffCallback = sinon.stub();
    const fakeWrapper = {
        on: sinon.stub().returns(wrapperOffCallback),
    } as any;
    let eventWrapperStub: sinon.SinonStub<any, any>;

    const getFakeEmitterCallbacks = () => {
        const callbacks: Record<string, Function> = {};
        fakeEmitter.on.getCalls().forEach((call: any) => {
            const [event, callback] = call.args;
            callbacks[event] = callback;
        });

        return callbacks;
    };
    const deferId = 123;

    const sandbox = sinon.createSandbox();
    beforeEach(() => {
        sandbox
            .stub(urlUtils, 'parseUrl')
            .callsFake((ctx: any, url: string) => ({ host: url } as any));
        setDeferStub = sandbox.stub(defer, 'setDefer').returns(deferId);
        clearDeferStub = sandbox.stub(defer, 'clearDefer');
        isIframeStub = sandbox.stub(browserUtils, 'isIframe').returns(true);
        sandbox.stub(eventsUtils, 'emitter').returns(fakeEmitter);
        eventWrapperStub = sandbox
            .stub(eventsUtils, 'cEvent')
            .returns(fakeWrapper);
    });

    afterEach(() => {
        sandbox.restore();

        fakeEmitter.on.resetHistory();
        fakeEmitter.off.resetHistory();
        fakeEmitter.trigger.resetHistory();
        wrapperOffCallback.resetHistory();
        fakeWrapper.on.resetHistory();
    });

    it('inits as master in iframe if postMessage on top is broken', () => {
        const ctx = {
            postMessage: () => {},
            parent: {},
            JSON,
            location: {
                host: 'example.com',
            },
        } as any;
        isIframeStub.returns(true);
        const recorder = {
            getFrameId: () => 0,
        } as any;
        const connector = getIframeConnector(ctx, recorder, []);
        chai.expect(connector.sendSlaveData).to.equal(noop);
        chai.expect(connector.stop).to.equal(noop);

        const [deferCtx, deferCallback, deferTimeout] =
            setDeferStub.getCall(0).args;
        chai.expect(deferCtx).to.equal(ctx);
        chai.expect(deferTimeout).to.equal(10);
        deferCallback();
        const [eventName, event] = fakeEmitter.trigger.getCall(0).args;
        chai.expect(eventName).to.equal(CONNECTOR_INITED);
        chai.expect(event).to.deep.equal({ isSlave: false });
    });

    it('inits as master if postMessage is broken', () => {
        const ctx = {
            JSON,
            location: {
                host: 'example.com',
            },
        } as any;
        isIframeStub.returns(false);
        const recorder = {
            getFrameId: () => 0,
        } as any;
        const connector = getIframeConnector(ctx, recorder, []);
        chai.expect(connector.sendSlaveData).to.equal(noop);
        chai.expect(connector.stop).to.equal(noop);

        const [deferCtx, deferCallback, deferTimeout] =
            setDeferStub.getCall(0).args;
        chai.expect(deferCtx).to.equal(ctx);
        chai.expect(deferTimeout).to.equal(10);
        deferCallback();
        const [eventName, event] = fakeEmitter.trigger.getCall(0).args;
        chai.expect(eventName).to.equal(CONNECTOR_INITED);
        chai.expect(event).to.deep.equal({ isSlave: false });
    });

    it('breakes if postMessage is broken and frameId is set', () => {
        const ctx = {
            JSON,
            location: {
                host: 'example.com',
            },
        } as any;
        isIframeStub.returns(false);
        const recorder = {
            getFrameId: () => 1,
        } as any;
        try {
            getIframeConnector(ctx, recorder, []);
        } catch (e) {
            chai.assert(e.message.startsWith(KNOWN_ERROR));
        }
    });

    it('subscribes to message event and triggers events of event emitter', () => {
        const postMessageStub = sinon.stub();
        const ctx = {
            postMessage: () => {},
            parent: {
                postMessage: postMessageStub,
            },
            JSON,
            location: {
                host: 'example.com',
            },
        } as any;
        const recorder = {
            getFrameId: () => 0,
        } as any;
        const trustedHosts = ['example.com'];
        const connector = getIframeConnector(ctx, recorder, trustedHosts);
        chai.assert(eventWrapperStub.calledWith(ctx));
        const [eventCtx, eventName, callback] = fakeWrapper.on.getCall(0).args;
        chai.expect(eventCtx).to.equal(ctx);
        chai.expect(eventName).to.deep.equal(['message']);

        callback({
            data: JSON.stringify({
                type: 'not-our-event-name',
            }),
        });
        chai.assert(fakeEmitter.trigger.notCalled);

        callback({
            source: 'some-source',
            origin: 'some-origin',
            data: JSON.stringify({
                type: SLAVE_REGISTER_EVENT_NAME,
                data: 'some-data',
            }),
        });
        const [event, eventObject] = fakeEmitter.trigger.getCall(0).args;
        chai.expect(event).to.deep.equal(SLAVE_REGISTER_EVENT_NAME);
        chai.expect({
            source: 'some-source',
            origin: 'some-origin',
            data: {
                type: SLAVE_REGISTER_EVENT_NAME,
                data: 'some-data',
            },
        }).to.deep.equal(eventObject);

        connector.stop();
        chai.assert(wrapperOffCallback.called);
    });

    it('registers itself as a slave if needed', () => {
        const postMessageStub = sinon.stub();
        const ctx = {
            parent: {
                postMessage: postMessageStub,
            },
            postMessage: () => {},
            JSON,
            location: {
                host: 'example.com',
            },
        } as any;
        const recorder = {
            getFrameId: () => 0,
        } as any;
        const trustedHosts = ['example.com'];
        getIframeConnector(ctx, recorder, trustedHosts);

        const [deferCtx, deferCallback, deferTimeout] =
            setDeferStub.getCall(0).args;
        chai.expect(deferCtx).to.equal(ctx);
        chai.expect(deferTimeout).to.equal(SLAVE_INIT_FREQUENCY);
        deferCallback();

        const [data, filter] = postMessageStub.getCall(0).args;
        chai.expect(filter).to.equal('*');
        chai.expect({
            type: SLAVE_REGISTER_EVENT_NAME,
        }).to.deep.equal(JSON.parse(data));

        const responseCallback =
            getFakeEmitterCallbacks()[
                SLAVE_REGISTER_PARENT_RESPONSE_EVENT_NAME
            ];
        responseCallback({
            origin: 'example.com',
            source: ctx.parent,
            data: {
                frameId: 100,
            },
        });

        const [name, callback] = fakeEmitter.off.getCall(0).args;
        chai.expect(name).to.deep.equal([
            SLAVE_REGISTER_PARENT_RESPONSE_EVENT_NAME,
        ]);
        chai.expect(callback).to.equal(responseCallback);
        chai.assert(clearDeferStub.calledWith(ctx, deferId));
        const [eventName, eventData] = fakeEmitter.trigger.getCall(0).args;
        chai.expect(eventName).to.equal(CONNECTOR_INITED);
        chai.expect(eventData).to.deep.equal({ frameId: 100, isSlave: true });
    });

    it('registers as a master if no response recieved', () => {
        const postMessageStub = sinon.stub();
        const ctx = {
            parent: {
                postMessage: postMessageStub,
            },
            postMessage: () => {},
            JSON,
            location: {
                host: 'example.com',
            },
        } as any;
        const recorder = {
            getFrameId: () => 0,
        } as any;
        const trustedHosts = ['example.com'];
        getIframeConnector(ctx, recorder, trustedHosts);

        let [deferCtx, deferCallback, deferTimeout] =
            setDeferStub.getCall(0).args;
        chai.expect(deferCtx).to.equal(ctx);
        chai.expect(deferTimeout).to.equal(SLAVE_INIT_FREQUENCY);
        deferCallback();

        const [data, filter] = postMessageStub.getCall(0).args;
        chai.expect(filter).to.equal('*');
        chai.expect({
            type: SLAVE_REGISTER_EVENT_NAME,
        }).to.deep.equal(JSON.parse(data));

        [deferCtx, deferCallback, deferTimeout] = setDeferStub.getCall(1).args;
        chai.expect(deferCtx).to.equal(ctx);
        chai.expect(deferTimeout).to.equal(SLAVE_REGISTRATION_TIMEOUT);
        deferCallback();

        const responseCallback =
            getFakeEmitterCallbacks()[
                SLAVE_REGISTER_PARENT_RESPONSE_EVENT_NAME
            ];
        const [eventNames, cb] = fakeEmitter.off.getCall(0).args;
        chai.expect(eventNames).to.deep.equal([
            SLAVE_REGISTER_PARENT_RESPONSE_EVENT_NAME,
        ]);
        chai.expect(cb).to.equal(responseCallback);
        chai.assert(clearDeferStub.calledWith(ctx, deferId));
        const [eventName, eventData] = fakeEmitter.trigger.getCall(0).args;
        chai.expect(eventName).to.equal(CONNECTOR_INITED);
        chai.expect(eventData).to.deep.equal({ isSlave: false });
    });

    it('responds to the slave registration event', () => {
        const postMessageStub = sinon.stub();
        const source = {
            postMessage: postMessageStub,
        };
        const iframe = { contentWindow: source };
        const querySelectorAllStub = sinon.stub().returns([iframe]);
        const indexNodeStub = sinon.stub().returns(100);
        const ctx = {
            postMessage: () => {},
            parent: {
                postMessage: () => {},
            },
            JSON,
            location: {
                host: 'example.com',
            },
            document: {
                querySelectorAll: querySelectorAllStub,
            },
        } as any;
        const recorder = {
            getFrameId: () => 0,
            getIndexer: () => ({
                indexNode: indexNodeStub,
            }),
        } as any;

        const trustedHosts = ['example.com'];
        isIframeStub.returns(false);
        getIframeConnector(ctx, recorder, trustedHosts);

        const slaveRgistrationCallback =
            getFakeEmitterCallbacks()[SLAVE_REGISTER_EVENT_NAME];
        slaveRgistrationCallback({
            source,
            origin: 'some-origin',
            data: {
                type: SLAVE_REGISTER_EVENT_NAME,
                data: 'some-data',
            },
        });
        chai.assert(querySelectorAllStub.calledWith('iframe'));
        chai.assert(indexNodeStub.calledWith(iframe));
        const [data, filter] = postMessageStub.getCall(0).args;
        chai.expect(filter).to.equal('*');
        chai.expect(JSON.parse(data)).to.deep.equal({
            type: SLAVE_REGISTER_PARENT_RESPONSE_EVENT_NAME,
            frameId: 100,
        });
    });

    it('sends slave data', () => {
        const postMessageStub = sinon.stub();
        const ctx = {
            postMessage: () => {},
            parent: {
                postMessage: postMessageStub,
            },
            JSON,
            location: {
                host: 'example.com',
            },
            document: {},
        } as any;
        const recorder = {
            getFrameId: () => 100,
        } as any;
        const connector = getIframeConnector(ctx, recorder, []);

        connector.sendSlaveData([
            {
                data: 'something-something',
            } as any,
        ]);
        const [data, filter] = postMessageStub.getCall(0).args;
        chai.expect(filter).to.equal('*');
        chai.expect(JSON.parse(data)).to.deep.equal({
            type: SLAVE_DATA_EVENT_NAME,
            frameId: 100,
            data: [
                {
                    data: 'something-something',
                },
            ],
        });
    });
});
