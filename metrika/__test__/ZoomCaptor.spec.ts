import Sinon, * as sinon from 'sinon';
import * as chai from 'chai';
import * as dom from '@src/utils/dom';
import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';
import { createRecorderMock } from '../../AbstractCaptor/__tests__/createMockRecorder';
import {
    ZoomCaptor,
    ZOOM_THROTTLE_TIMEOUT,
    ZOOM_EVENT_NAME,
} from '../ZoomCaptor';

describe('ZoomCaptor', () => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const sandbox = sinon.createSandbox();
    let getVisualViewportSizeStub: Sinon.SinonStub<any, any>;
    let getDocumentScrollStub: Sinon.SinonStub<any, any>;
    let recorder: any;

    beforeEach(() => {
        recorder = createRecorderMock();
        getVisualViewportSizeStub = sandbox
            .stub(dom, 'getVisualViewportSize')
            .returns(null);
        getDocumentScrollStub = sandbox
            .stub(dom, 'getDocumentScroll')
            .returns({ x: 0, y: 0 });
    });

    afterEach(() => {
        sandbox.restore();
        recorder.test.restore();
    });

    it('does nothing if visual viewport is not present', () => {
        const ctx: any = {};
        getVisualViewportSizeStub.returns(null);
        const zoomCaptor = new ZoomCaptor(ctx, recorder, 'a');
        zoomCaptor.start();
        sinon.assert.notCalled(recorder.getEventWrapper().on);
        sinon.assert.notCalled(recorder.sendEventObject);
    });

    it('captures zoom', () => {
        const ctx: any = {
            visualViewport: {},
        };
        getVisualViewportSizeStub.returns([100, 100, 2]);
        const zoomCaptor = new ZoomCaptor(ctx, recorder, 'a');
        // initial zoom
        zoomCaptor.start();
        chai.expect(
            recorder.test.createThrottledFunctionSpy.getCall(0).args[1],
        ).to.equal(ZOOM_THROTTLE_TIMEOUT);
        const [target, eventName, callback] = recorder
            .getEventWrapper()
            .on.getCall(0).args;
        chai.expect(target).to.equal(ctx.visualViewport);
        chai.expect(eventName).to.deep.equal(['resize']);
        let [type, data, name] = recorder.sendEventObject.getCall(0).args;
        chai.expect(type).to.equal(EVENT_EVENT_TYPE);
        chai.expect(data).to.deep.equal({
            level: 2,
            x: 0,
            y: 0,
        });
        chai.expect(name).to.equal(ZOOM_EVENT_NAME);
        // changed zoom
        getVisualViewportSizeStub.returns([100, 100, 1]);
        getDocumentScrollStub.returns({ x: 100, y: 100 });
        callback();
        [type, data, name] = recorder.sendEventObject.getCall(1).args;
        chai.expect(type).to.equal(EVENT_EVENT_TYPE);
        chai.expect(data).to.deep.equal({
            level: 1,
            x: 100,
            y: 100,
        });
        chai.expect(name).to.equal(ZOOM_EVENT_NAME);
        // unsubscribing
        zoomCaptor.stop();
        sinon.assert.called(recorder.test.flushSpy);
        sinon.assert.called(recorder.test.offEventSpy);
    });
});
