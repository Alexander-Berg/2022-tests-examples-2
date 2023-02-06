import * as sinon from 'sinon';
import * as chai from 'chai';
import * as fnModule from '@src/utils/function';
import { SelectionCaptor, SELECTION_EVENTS } from '../SelectionCaptor';

describe('SelectionCaptor', () => {
    const sandbox = sinon.createSandbox();
    let toNativeOrFalseStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        toNativeOrFalseStub = sandbox.stub(fnModule, 'toNativeOrFalse');
        toNativeOrFalseStub.callsFake((fn) => {
            return fn;
        });
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('Handles selection and from one element to page and then cancelation', () => {
        const endSelectionElement = {
            id: 321,
        };
        const inputElement = {
            type: 'text',
            id: 123,
            selectionStart: 100,
            selectionEnd: 900,
        };
        const ctx: any = {
            getSelection: () => ({
                getRangeAt: () => ({
                    startOffset: 200,
                    endOffset: 300,
                    startContainer: inputElement,
                    endContainer: endSelectionElement,
                }),
                rangeCount: 1,
            }),
        };
        const indexer: any = {
            indexNode: sinon.stub().callsFake((node: any) => node.id),
        };
        const offCallback = sinon.stub();
        const eventWrapper = {
            on: sinon.stub().returns(offCallback),
        };
        const recorder: any = {
            getEventWrapper: () => eventWrapper,
            getIndexer: () => indexer,
            sendEventObject: sinon.stub(),
        };
        const captor = new SelectionCaptor(ctx, recorder, 'a');
        captor.start();
        const [page, pageEvents, callback] = eventWrapper.on.getCall(0).args;
        chai.expect(page).to.equal(ctx);
        chai.expect(pageEvents).to.deep.equal(SELECTION_EVENTS);

        let event: any = {
            type: 'select',
            target: inputElement,
        };
        callback(event);

        let [type, data, eventName] = recorder.sendEventObject.getCall(0).args;

        // Input selection
        chai.expect(type).to.equal('event');
        chai.expect(eventName).to.equal('selection');
        chai.expect(data).to.deep.equal({
            start: 100,
            end: 900,
            target: 123,
        });

        // Page selection
        event = {
            type: 'mousemove',
            which: 1,
        };
        callback(event);
        [type, data, eventName] = recorder.sendEventObject.getCall(1).args;
        chai.expect(type).to.equal('event');
        chai.expect(eventName).to.equal('selection');
        chai.expect(data).to.deep.equal({
            start: 200,
            end: 300,
            startNode: 123,
            endNode: 321,
        });

        // Selection cancelation
        inputElement.selectionEnd = 0;
        inputElement.selectionStart = 0;
        event = {
            type: 'select',
            target: inputElement,
        };
        callback(event);
        [type, data, eventName] = recorder.sendEventObject.getCall(2).args;
        chai.expect(type).to.equal('event');
        chai.expect(eventName).to.equal('selection');
        chai.expect(data).to.deep.equal({
            start: 0,
            end: 0,
        });

        captor.stop();
        sinon.assert.calledOnce(offCallback);
    });
});
