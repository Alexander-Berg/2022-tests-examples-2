import chai from 'chai';
import * as sinon from 'sinon';
import * as Time from '@src/utils/time';
import * as globalStorage from '@src/storage/global';
import * as browserUtils from '@src/utils/browser';
import { WEBVISOR2_IFRAME_SUPPORT } from '@generated/features';
import { flags } from '@inject';
import * as captors from '../captors';
import * as browser from '../components/Browser';
import * as pageInfo from '../components/PageInfo';
import * as Indexer from '../indexer/Indexer';
import * as transform from '../eventsTransformer';
import * as connector from '../components/IframeConnector';
import { WEBVISOR_ENABLED_GLOBAL_KEY } from '../consts';
import { Recorder } from '../Recorder';

describe('Recorder', () => {
    const captorStart = sinon.stub();
    const captorStop = sinon.stub();
    class FakeCaptor {
        start: Function;

        stop: Function;

        constructor() {
            this.start = captorStart;
            this.stop = captorStop;
        }
    }

    const indexerStart = sinon.stub();
    const indexerStop = sinon.stub();
    const indexerHandleNodesAdd = sinon.stub();
    class FakeIndexer {
        start: Function;

        stop: Function;

        handleNodesAdd: Function;

        constructor() {
            this.handleNodesAdd = indexerHandleNodesAdd;
            this.start = indexerStart;
            this.stop = indexerStop;
        }
    }

    const iframeConnectorEmitter = {
        on: sinon.stub(),
        off: sinon.stub(),
    };
    const iframeConnector = {
        stop: sinon.stub(),
        sendSlaveData: sinon.stub(),
        getEmitter: () => iframeConnectorEmitter,
    };
    const fakeGlobalStorage = {
        getVal: sinon.stub(),
        setVal: sinon.stub(),
    };

    let isIframeStub: sinon.SinonStub<any, any>;
    let getGlobalStorageStub: sinon.SinonStub<any, any>;
    let transfromerStub: sinon.SinonStub<any, any>;
    let indexerStub: sinon.SinonStub<any, any>;
    let timeStub: sinon.SinonStub<any, any>;
    let browserStub: sinon.SinonStub<any, any>;
    let pageInfoStub: sinon.SinonStub<any, any>;
    let iframeConnectorStub: sinon.SinonStub<any, any>;

    const fakeBrowser = {
        getViewportSize: () => [100, 100],
    };
    const fakePage = {
        getBase: () => 'base',
        getDoctype: () => 'html',
        getTabId: () => '12312313',
    };

    const ctx = {
        location: {
            href: 'http://example.com/some-path',
            protocol: 'http',
            host: 'example.com',
            path: 'some-path',
        },
        navigator: {
            userAgent: 'ua',
        },
        screen: {
            width: 20,
            height: 30,
        },
        document: {
            title: 'title',
            referrer: 'ref',
            documentElement: {},
            body: {},
        },
        Math,
    } as any;

    beforeEach(() => {
        isIframeStub = sinon.stub(browserUtils, 'isIframe');
        getGlobalStorageStub = sinon
            .stub(globalStorage, 'getGlobalStorage')
            .returns(fakeGlobalStorage as any);
        iframeConnectorStub = sinon
            .stub(connector, 'getIframeConnector')
            .returns(iframeConnector as any);
        transfromerStub = sinon
            .stub(transform, 'transformItem')
            .callsFake((data) => {
                return data;
            });
        indexerStub = sinon
            .stub(Indexer, 'Indexer')
            .callsFake(FakeIndexer as any);
        timeStub = sinon.stub(Time, 'Time').returns(() => 100 as any);
        browserStub = sinon
            .stub(browser, 'getBrowser')
            .returns(fakeBrowser as any);
        pageInfoStub = sinon
            .stub(pageInfo, 'getPageInfo')
            .returns(fakePage as any);
    });

    afterEach(() => {
        captorStart.resetHistory();
        captorStop.resetHistory();
        iframeConnectorEmitter.on.resetHistory();
        iframeConnectorEmitter.off.resetHistory();
        iframeConnector.sendSlaveData.resetHistory();
        iframeConnector.stop.resetHistory();
        indexerStart.resetHistory();
        indexerStop.resetHistory();
        fakeGlobalStorage.setVal.resetHistory();
        fakeGlobalStorage.getVal.resetHistory();
        indexerHandleNodesAdd.resetHistory();

        isIframeStub.restore();
        getGlobalStorageStub.restore();
        iframeConnectorStub.restore();
        transfromerStub.restore();
        indexerStub.restore();
        timeStub.restore();
        browserStub.restore();
        pageInfoStub.restore();
    });

    const slaveFrameId = 100;
    const event = {
        stamp: 100,
        type: 'windowfocus',
        frameId: 0,
        data: {},
    } as any;
    const slaveEvent = {
        ...event,
        frameId: slaveFrameId,
    };

    it('has the correct lifecycle without frame support', () => {
        (flags as any)[WEBVISOR2_IFRAME_SUPPORT] = false;
        captors.captors.splice(0);
        captors.captors.push([FakeCaptor as any, 'a']);
        fakeGlobalStorage.getVal.returns(false);

        const recorder = new Recorder(ctx, { isEU: false });
        chai.assert(
            fakeGlobalStorage.getVal.calledWith(WEBVISOR_ENABLED_GLOBAL_KEY),
        );
        chai.assert(
            fakeGlobalStorage.setVal.calledWith(
                WEBVISOR_ENABLED_GLOBAL_KEY,
                true,
            ),
        );
        recorder.sendData(event);

        // Start is called and we should send page
        const senderFunction = sinon.stub();
        recorder.start(senderFunction);

        chai.assert(indexerStart.called);
        chai.assert(captorStart.called);

        const [data] = senderFunction.getCall(0).args;
        chai.expect([event]).to.deep.equal(data);

        // Stops when stop is called
        recorder.stop();
        chai.assert(captorStop.called);
        chai.assert(indexerStop.called);
    });

    it('throws error when webvisor enabled flag is true', () => {
        fakeGlobalStorage.getVal.returns(true);
        chai.expect(() => new Recorder(ctx, { isEU: false })).throws();
    });

    it('has the correct lifecycle with iframe support as explicitly created as a slave', () => {
        (flags as any)[WEBVISOR2_IFRAME_SUPPORT] = true;
        captors.captors.splice(0);
        captors.captors.push([FakeCaptor as any, 'a']);
        fakeGlobalStorage.getVal.returns(false);
        isIframeStub.returns(true);

        const recorder = new Recorder(ctx, { isEU: false, frameId: 100 });
        chai.assert(
            fakeGlobalStorage.getVal.calledWith(WEBVISOR_ENABLED_GLOBAL_KEY),
        );
        chai.assert(
            fakeGlobalStorage.setVal.calledWith(
                WEBVISOR_ENABLED_GLOBAL_KEY,
                true,
            ),
        );
        recorder.sendData(event);

        // Start is called and we should send page
        const senderFunction = sinon.stub();

        recorder.start(senderFunction);

        chai.assert(indexerStart.called);
        chai.assert(captorStart.called);

        chai.assert(senderFunction.notCalled);
        const [data] = iframeConnector.sendSlaveData.getCall(0).args;
        chai.expect([slaveEvent]).to.deep.equal(data);

        // Stops when stop is called
        recorder.stop();
        chai.assert(iframeConnector.stop.called);
        chai.assert(captorStop.called);
        chai.assert(indexerStop.called);
    });

    it('has the correct lifecycle with iframe support as master', () => {
        (flags as any)[WEBVISOR2_IFRAME_SUPPORT] = true;
        captors.captors.splice(0);
        captors.captors.push([FakeCaptor as any, 'a']);
        fakeGlobalStorage.getVal.returns(false);
        isIframeStub.returns(true);

        const recorder = new Recorder(ctx, { isEU: false });
        chai.assert(
            fakeGlobalStorage.getVal.calledWith(WEBVISOR_ENABLED_GLOBAL_KEY),
        );
        chai.assert(
            fakeGlobalStorage.setVal.calledWith(
                WEBVISOR_ENABLED_GLOBAL_KEY,
                true,
            ),
        );

        const [[eventKey], registrationCallback] =
            iframeConnectorEmitter.on.getCall(0).args;
        chai.expect(eventKey).to.equal(connector.CONNECTOR_INITED);

        chai.assert(indexerStart.called);
        chai.assert(captorStart.called);
        recorder.sendData(event);

        // Start is called and we shouldn't send page
        // because we are waiting for iframe connection
        const senderFunction = sinon.stub();
        recorder.start(senderFunction);
        chai.assert(senderFunction.notCalled);

        // Inited as master and we should start recording
        registrationCallback({
            isSlave: false,
        });
        const [data] = senderFunction.getCall(0).args;
        chai.expect([event]).to.deep.equal(data);

        // Stops when stop is called
        recorder.stop();
        chai.assert(captorStop.called);
        chai.assert(indexerStop.called);
    });

    it('has the correct lifecycle with iframe support as a slave', () => {
        (flags as any)[WEBVISOR2_IFRAME_SUPPORT] = true;
        captors.captors.splice(0);
        captors.captors.push([FakeCaptor as any, 'a']);
        fakeGlobalStorage.getVal.returns(false);
        isIframeStub.returns(true);

        const recorder = new Recorder(ctx, { isEU: false });
        chai.assert(
            fakeGlobalStorage.getVal.calledWith(WEBVISOR_ENABLED_GLOBAL_KEY),
        );
        chai.assert(
            fakeGlobalStorage.setVal.calledWith(
                WEBVISOR_ENABLED_GLOBAL_KEY,
                true,
            ),
        );
        const [[eventKey], registrationCallback] =
            iframeConnectorEmitter.on.getCall(0).args;
        chai.expect(eventKey).to.equal(connector.CONNECTOR_INITED);

        chai.assert(indexerStart.called);
        chai.assert(captorStart.called);
        recorder.sendData(event);

        // Start is called and we shouldn't send page
        // because we are waiting for iframe connection
        const senderFunction = sinon.stub();
        recorder.start(senderFunction);
        chai.assert(senderFunction.notCalled);

        // Inited as master and we should start recording
        registrationCallback({
            isSlave: true,
            frameId: slaveFrameId,
        });
        const [data] = iframeConnector.sendSlaveData.getCall(0).args;
        chai.expect([slaveEvent]).to.deep.equal(data);

        // Stops when stop is called
        recorder.stop();
        chai.assert(captorStop.called);
        chai.assert(indexerStop.called);
    });
});
