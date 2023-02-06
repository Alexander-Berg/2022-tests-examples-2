import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';
import { WindowFocusCaptor } from '../WindowFocusCaptor';
import { createRecorderMock } from '../../AbstractCaptor/__tests__/createMockRecorder';

describe('WindowFocusCaptor', () => {
    let recorder: any;

    beforeEach(() => {
        recorder = createRecorderMock();
    });

    afterEach(() => {
        recorder.test.restore();
    });

    const hiddenTest = (hiddenName: string, eventName: string) => {
        const win = {
            document: { [hiddenName]: false },
        } as any;
        const windowFocusCaptor = new WindowFocusCaptor(win, recorder, 'a');
        windowFocusCaptor.start();

        ['blur', 'focus'].forEach((item, i) => {
            win.document[hiddenName] = item === 'blur';

            recorder.test.createEvent(eventName, {
                type: eventName,
            });

            recorder.test.checkSendEvent(
                EVENT_EVENT_TYPE,
                {},
                `window${item}`,
                i,
            );
        });
    };

    it('document.hidden', () => {
        hiddenTest('hidden', 'visibilitychange');
    });

    it('document.msHidden', () => {
        hiddenTest('msHidden', 'msvisibilitychange');
    });

    it('document.webkitHidden', () => {
        hiddenTest('webkitHidden', 'webkitvisibilitychange');
    });

    it('focus, blur', () => {
        const windowFocusCaptor = new WindowFocusCaptor(
            { document: {} } as any,
            recorder,
            'a',
        );
        windowFocusCaptor.start();

        recorder.test.createEvent('blur', {
            type: 'blur',
        });

        recorder.test.checkSendEvent(EVENT_EVENT_TYPE, {}, 'windowblur');
    });
});
