import * as sinon from 'sinon';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';
import { MouseCaptor } from '../MouseCaptor';
import { createRecorderMock } from '../../AbstractCaptor/__tests__/createMockRecorder';

describe('MouseCaptor', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const elementFromPoint = document.createElement('span');
    const target = document.createElement('div');
    const event = {
        clientX: 10,
        clientY: 10,
    };

    const win: any = {
        document: {
            elementFromPoint: sinon.spy(() => elementFromPoint),
        },
    };
    let recorder: any;

    beforeEach(() => {
        recorder = createRecorderMock();
    });

    afterEach(() => {
        win.document.elementFromPoint.resetHistory();
        recorder.test.restore();
    });

    it('MouseCaptor - throttleManager usage', () => {
        const mouseCaptor = new MouseCaptor(win, recorder, 'a');
        mouseCaptor.start();
        recorder.test.checkThrottleManagerUsage(win);
        mouseCaptor.stop();
        sinon.assert.called(recorder.test.flushSpy);
    });

    it('mousemove handler', () => {
        const mouseCaptor = new MouseCaptor(win, recorder, 'a');
        mouseCaptor.start();
        recorder.test.createEvent('mousemove', {
            clientX: event.clientX,
            clientY: event.clientY,
            type: 'mousemove',
        });
        sinon.assert.calledWith(
            win.document.elementFromPoint,
            event.clientX,
            event.clientY,
        );
        recorder.test.checkCallThrottledHandler();
        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                x: 10,
                y: 10,
                target: elementFromPoint,
            },
            'mousemove',
        );
    });

    it('mousedown handler', () => {
        const mouseCaptor = new MouseCaptor(win, recorder, 'a');
        mouseCaptor.start();
        recorder.test.createEvent('mousedown', {
            target,
            type: 'mousedown',
            clientX: event.clientX,
            clientY: event.clientY,
        });
        recorder.test.checkCallOriginalHandler();

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                x: event.clientX,
                y: event.clientY,
                target,
            },
            'mousedown',
        );
    });
});
