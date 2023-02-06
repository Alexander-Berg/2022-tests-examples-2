import * as chai from 'chai';
import * as sinon from 'sinon';
import * as urlUtils from '@src/utils/url';
import * as waitFB from '@src/utils/dom/waitForBody';
import * as task from '@src/utils/async';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import { IframeCaptor } from '../IframeCaptor';
import { NODE_ADD_EVENT_KEY_PREFIX } from '../../../indexer/Indexer';
import { SLAVE_DATA_RECIEVED } from '../../../components/IframeConnector';

describe('IframeCaptor', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const indexerOnStub = sinon.stub();
    const fakeIndexer = {
        on: indexerOnStub,
    } as any;
    const connectorOnStub = sinon.stub();
    const fakeIframeConnector = {
        getEmitter: () => ({
            on: connectorOnStub,
        }),
    };
    const sandbox = sinon.createSandbox();
    const recordStamp = 100;
    const sendData = sinon.stub();
    const slaveRecorderStopStub = sinon.stub();
    const createSlaveRecorder = sinon.stub().returns({
        stop: slaveRecorderStopStub,
    } as any);
    const recorder = {
        getOptions: () => ({ childIframe: true }),
        getIndexer: () => fakeIndexer,
        getIframeConnector: () => fakeIframeConnector,
        createSlaveRecorder,
        sendData,
        getRecordStamp: () => recordStamp,
        getEventWrapper: () => ({}),
    } as any;

    beforeEach(() => {
        sandbox.stub(task, 'taskFork').callsFake((rej, resolve) => resolve);
        sandbox.stub(waitFB, 'waitForBodyTask').callsFake(((win: any) => {
            chai.expect(win).to.equal(window);
            return (cb: Function) => {
                cb();
            };
        }) as any);
        sandbox
            .stub(urlUtils, 'parseUrl')
            .callsFake((_: any, host: string) => ({ host } as any));
    });

    afterEach(() => {
        sandbox.restore();
        createSlaveRecorder.resetHistory();
        connectorOnStub.resetHistory();
        indexerOnStub.resetHistory();
        slaveRecorderStopStub.resetHistory();
    });

    it("Creates slave recorder in blank or same origin frame and doesn't in different origin, and calls stop", () => {
        const captor = new IframeCaptor(window, recorder, 'a');
        captor.start();
        const [node, event, callback] = indexerOnStub.getCall(0).args;
        chai.expect(event).to.equal(NODE_ADD_EVENT_KEY_PREFIX);
        chai.expect(node).to.equal('iframe');

        const invalidBlankIframe = document.createElement('iframe');
        invalidBlankIframe.setAttribute('src', 'about:blank');
        invalidBlankIframe.setAttribute('sandbox', 'no-no-no');
        callback({ data: { node: invalidBlankIframe } });
        chai.assert(createSlaveRecorder.notCalled);

        const differentOriginIframe = document.createElement('iframe');
        differentOriginIframe.setAttribute('src', 'some-different-origin.org');
        callback({ data: { node: differentOriginIframe } });
        chai.assert(createSlaveRecorder.notCalled);

        const blankIframe = document.createElement('iframe');
        blankIframe.setAttribute('src', 'about:blank');
        blankIframe.setAttribute('sandbox', 'allow-same-origin');
        document.body.append(blankIframe);
        callback({ data: { node: blankIframe, id: 100 } });
        createSlaveRecorder.calledWith(blankIframe.contentWindow, 100);
        createSlaveRecorder.resetHistory();

        const sameOriginIframe = document.createElement('iframe');
        sameOriginIframe.setAttribute('src', 'example.com');
        createSlaveRecorder.calledWith(sameOriginIframe.contentWindow, 100);

        captor.stop();
        sinon.assert.called(slaveRecorderStopStub);
    });

    it('Updates slave data stamps and sends events afterwards', () => {
        const captor = new IframeCaptor(window, recorder, 'a');
        captor.start();
        const [[event], callback] = connectorOnStub.getCall(0).args;
        chai.expect(event).to.equal(SLAVE_DATA_RECIEVED);

        callback({
            frameId: 1,
            data: [
                {
                    frameId: 1,
                    stamp: 100,
                    type: 'event',
                    event: 'someEvent',
                },
                {
                    frameId: 1,
                    stamp: 200,
                    type: 'event',
                    event: 'someEvent1',
                },
            ],
        });
        chai.assert(sendData.notCalled);
        callback({
            frameId: 1,
            data: [
                {
                    event: 'page',
                    type: 'page',
                    frameId: 1,
                    stamp: 0,
                    data: {
                        recordStamp: 200,
                    },
                },
            ],
        });
        const [data] = sendData.getCall(0).args;

        chai.expect(data).to.be.deep.eq([
            {
                frameId: 1,
                stamp: 200,
                type: 'event',
                event: 'someEvent',
            },
            {
                frameId: 1,
                stamp: 300,
                type: 'event',
                event: 'someEvent1',
            },
            {
                event: 'page',
                type: 'page',
                frameId: 1,
                stamp: 100,
                data: {
                    recordStamp: 200,
                },
            },
        ]);
    });
});
