import * as chai from 'chai';
import * as sinon from 'sinon';
import * as throttle from '@private/src/providers/webvisor2/recorder/utils/ThrottleManager';
import { ScrollCaptor } from '../ScrollCaptor';

describe('ScrollCaptor', () => {
    const sandbox = sinon.createSandbox();
    const flushStub = sinon.stub();
    const offStub = sinon.stub();
    const createThrottledFunctionStub = sinon
        .stub()
        .callsFake((fn: Function) => {
            return fn;
        });
    const fakeEventWrapper = {
        on: sinon.stub().returns(offStub),
    };
    const fakeIndexer = {
        indexNode: sinon.stub(),
    };
    class FakeThrottleManager {
        createThrottledFunction = createThrottledFunctionStub;

        flush = flushStub;
    }

    beforeEach(() => {
        sandbox
            .stub(throttle, 'ThrottleManager')
            .callsFake(FakeThrottleManager as any);
    });

    afterEach(() => {
        sandbox.restore();
        flushStub.resetHistory();
        fakeEventWrapper.on.resetHistory();
        fakeIndexer.indexNode.resetHistory();
        createThrottledFunctionStub.resetHistory();
        offStub.resetHistory();
    });

    it('Captures scroll', () => {
        const ctx: any = {
            scrollX: 100,
            scrollY: 200,
            document: {
                documentElement: {},
                body: {},
            },
        };
        const scrollingElement = {
            scrollTop: 300,
            scrollLeft: 400,
        };
        const browser = {
            isAndroid: () => false,
            getScrollingElement: () => scrollingElement,
        };
        const recorder: any = {
            getBrowser: () => browser,
            getEventWrapper: () => fakeEventWrapper,
            getIndexer: () => fakeIndexer,
            sendEventObject: sinon.stub(),
        };
        const captor = new ScrollCaptor(ctx, recorder, 'a');
        captor.start();

        // Initial scroll
        let [type, data, event] = recorder.sendEventObject.getCall(0).args;
        chai.expect(type).to.equal('event');
        chai.expect(event).to.equal('scroll');
        chai.expect({
            x: 100,
            y: 200,
            page: true,
            target: -1,
        }).to.deep.equal(data);

        const [target, [eventName], callback] =
            fakeEventWrapper.on.getCall(0).args;
        chai.expect(target).to.equal(ctx);
        chai.expect(eventName).to.equal('scroll');

        // Page scroll
        const pageScrollEvent = {
            type: 'scroll',
            target: scrollingElement,
        };
        callback(pageScrollEvent);
        sinon.assert.calledOnce(createThrottledFunctionStub);

        [type, data, event] = recorder.sendEventObject.getCall(1).args;
        chai.expect(type).to.equal('event');
        chai.expect(event).to.equal('scroll');
        chai.expect({
            x: 400,
            y: 300,
            page: true,
            target: -1,
        }).to.deep.equal(data);

        // Page scroll to be ignored
        const ignoredPageScrollEvent = {
            type: 'scroll',
            target: scrollingElement,
        };
        callback(ignoredPageScrollEvent);
        sinon.assert.calledOnce(createThrottledFunctionStub);
        sinon.assert.calledTwice(recorder.sendEventObject);

        // Elements scroll
        fakeIndexer.indexNode.returns(123);
        const elementScrollTarget = {
            scrollLeft: 40,
            scrollTop: 50,
            ownerDocument: ctx.document,
        };
        const eleemntScrollEvent = {
            target: elementScrollTarget,
            type: 'scroll',
        };
        callback(eleemntScrollEvent);
        sinon.assert.calledTwice(createThrottledFunctionStub);

        [type, data, event] = recorder.sendEventObject.getCall(2).args;
        chai.expect(type).to.equal('event');
        chai.expect(event).to.equal('scroll');
        chai.expect({
            x: 40,
            y: 50,
            page: false,
            target: 123,
        }).to.deep.equal(data);

        captor.stop();
        sinon.assert.calledOnce(flushStub);
        sinon.assert.calledOnce(offStub);
    });
});
