import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';
import { FocusCaptor } from '../FocusCaptor';
import { createRecorderMock } from '../../AbstractCaptor/__tests__/createMockRecorder';

describe('FocusCaptor', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    let recorder: any;

    beforeEach(() => {
        recorder = createRecorderMock();
    });

    afterEach(() => {
        recorder.test.restore();
    });

    it('pointer event handler', () => {
        const target = document.createElement('input');
        const focusCaptor = new FocusCaptor(window, recorder, 'a');
        focusCaptor.start();
        recorder.test.createEvent('focus', {
            target,
            type: 'focus',
        });

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                target,
            },
            'focus',
        );
    });
});
