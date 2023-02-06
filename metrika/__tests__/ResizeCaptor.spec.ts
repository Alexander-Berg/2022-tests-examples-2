import * as sinon from 'sinon';
import * as chai from 'chai';
import * as defer from '@src/utils/defer';
import * as dom from '@src/utils/dom';
import {
    ResizeCaptor,
    RESIZE_EVENT_NAME,
    ROTATION_EVENT_NAME,
} from '../ResizeCaptor';
import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';

describe('ResizeCaptor', () => {
    const sandbox = sinon.createSandbox();
    let setDeferStub: sinon.SinonStub<any, any>;
    let getViewportSizeStub: sinon.SinonStub<any, any>;

    beforeEach(() => {
        setDeferStub = sandbox.stub(defer, 'setDefer');
        getViewportSizeStub = sandbox.stub(dom, 'getViewportSize');
    });

    afterEach(() => {
        sandbox.restore();
        setDeferStub.restore();
    });

    it('Captures initial resize and skips resize after rotation', () => {
        const fakeCtx: any = {
            Array,
        };
        const fakeEventWrapper = {
            on: sinon.stub(),
        };
        let orientation = 0;
        const fakeBrowser = {
            getScrollingElement: () => ({
                scrollWidth: 200,
                scrollHeight: 200,
            }),
            getOrientation: () => orientation,
        };
        getViewportSizeStub.returns([0, 0]);
        const stamp = 100;
        const fakeRecorder: any = {
            getEventWrapper: () => fakeEventWrapper,
            sendEventObject: sinon.stub(),
            getIndexer: () => ({}),
            getBrowser: () => fakeBrowser,
            stamp: () => stamp,
        };

        const captor = new ResizeCaptor(fakeCtx, fakeRecorder, 'a');

        // Initial resize
        captor.start();

        const events: Record<string, Function> = {};
        fakeEventWrapper.on.getCalls().forEach((call: any) => {
            const [ctx, name, callback] = call.args;
            chai.expect(ctx).to.equal(fakeCtx);
            events[name] = callback;
        });

        chai.assert(fakeRecorder.sendEventObject.notCalled);
        const [ctx, callback, timeout] = setDeferStub.getCall(0).args;
        chai.expect(ctx).to.equal(fakeCtx);
        chai.expect(timeout).to.equal(300);

        getViewportSizeStub.returns([100, 200]);
        callback();

        let [eventType, data, event] =
            fakeRecorder.sendEventObject.getCall(0).args;
        chai.expect(eventType).to.eq(EVENT_EVENT_TYPE);
        chai.expect(event).to.equal(RESIZE_EVENT_NAME);
        chai.expect(data).to.deep.equal({
            width: 100,
            height: 200,
            pageWidth: 200,
            pageHeight: 200,
        });

        // Regular resize
        getViewportSizeStub.returns([50, 100]);
        events.resize();
        [eventType, data, event] = fakeRecorder.sendEventObject.getCall(1).args;
        chai.expect(eventType).to.eq(EVENT_EVENT_TYPE);
        chai.expect(event).to.equal(RESIZE_EVENT_NAME);
        chai.expect(data).to.deep.equal({
            width: 50,
            height: 100,
            pageWidth: 200,
            pageHeight: 200,
        });

        // Rotation
        orientation = 90;
        getViewportSizeStub.returns([100, 100]);
        events.orientationchange();
        [eventType, data, event] = fakeRecorder.sendEventObject.getCall(2).args;
        chai.expect(eventType).to.eq(EVENT_EVENT_TYPE);
        chai.expect(event).to.equal(ROTATION_EVENT_NAME);
        chai.expect(data).to.deep.equal({
            width: 100,
            height: 100,
            orientation: 90,
        });
        fakeRecorder.sendEventObject.resetHistory();

        // This should be ignored because size and rotation are not change
        events.resize();
        events.orientationchange();
        chai.assert(fakeRecorder.sendEventObject.notCalled);
    });
});
