import * as sinon from 'sinon';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';
import { SrcsetLoadCaptor } from '../SrcsetLoadCaptor';
import { createRecorderMock } from '../../AbstractCaptor/__tests__/createMockRecorder';

describe('SrcsetLoadCaptor', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const win: any = {};
    let recorder: any;

    beforeEach(() => {
        recorder = createRecorderMock();
    });

    afterEach(() => {
        recorder.test.restore();
    });

    it('load handler', () => {
        const target = document.createElement('img');
        target.setAttribute('srcset', 'srcset');

        const srcsetLoadCaptor = new SrcsetLoadCaptor(win, recorder, 'a');
        srcsetLoadCaptor.start();
        recorder.test.createEvent('load', { target, type: 'load' });

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                target,
                value: target.currentSrc,
            },
            'srcset',
        );
    });

    it('incorrect target', () => {
        const target = document.createElement('div');

        const srcsetLoadCaptor = new SrcsetLoadCaptor(win, recorder, 'a');
        srcsetLoadCaptor.start();
        recorder.test.createEvent('load', { target });

        sinon.assert.notCalled(recorder.test.sendEventObjectSpy);
    });
});
