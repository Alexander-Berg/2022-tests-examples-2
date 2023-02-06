import sinon from 'sinon';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import { createRecorderMock } from '../../AbstractCaptor/__tests__/createMockRecorder';
import {
    KEY_DICT,
    KeyStrokeCaptor,
    MAC_OS_KEY,
    MODIFIER_CODES,
    OTHER_OS_KEY,
} from '../KeyStrokeCaptor';
import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';

describe('KeyStrokeCaptor', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const CTRL = 17;
    const A = 65;
    const LEFT_ARROW = 37;

    let recorder: any;
    let keyStrokeCaptor: any;
    let win: any;

    beforeEach(() => {
        win = {
            document: {},
            clearTimeout: window.clearTimeout.bind(window),
            setTimeout: window.setTimeout.bind(window),
        };
        recorder = createRecorderMock();
    });

    afterEach(() => {
        keyStrokeCaptor.stop();
        recorder.test.restore();
    });

    const focus = (tag: string, type?: string, className?: string) => {
        const element = document.createElement(tag);
        if (type) {
            (element as any).type = type;
        }
        if (className) {
            element.classList.add(className);
        }
        win.document.activeElement = element;

        return element;
    };

    it('send single key press', () => {
        keyStrokeCaptor = new KeyStrokeCaptor(win, recorder, 'a');
        keyStrokeCaptor.start();

        const input = focus('input');
        recorder.test.createEvent('keydown', {
            keyCode: LEFT_ARROW,
            target: input,
        });
        recorder.test.createEvent('keyup', {
            keyCode: LEFT_ARROW,
            target: input,
        });

        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                keystrokes: [
                    {
                        id: LEFT_ARROW,
                        key: KEY_DICT.multi[LEFT_ARROW],
                        isMeta: false,
                        modifier: undefined,
                    },
                ],
            },
            'keystroke',
        );
    });

    const ctrlTest = (os: string, appVersion: string) => (done: Mocha.Done) => {
        win.navigator = { appVersion };
        keyStrokeCaptor = new KeyStrokeCaptor(win, recorder, 'a');
        keyStrokeCaptor.start();
        const textarea = focus('textarea');

        recorder.test.createEvent('keydown', {
            keyCode: CTRL,
            target: textarea,
        });
        recorder.test.createEvent('keydown', { keyCode: A, target: textarea });
        setTimeout(() => {
            recorder.test.createEvent('keyup', {
                keyCode: A,
                target: textarea,
            });
            recorder.test.checkSendEvent(
                EVENT_EVENT_TYPE,
                {
                    keystrokes: [
                        {
                            id: CTRL,
                            key: KEY_DICT[os][CTRL],
                            isMeta: os === MAC_OS_KEY,
                            modifier: MODIFIER_CODES[CTRL],
                        },
                        {
                            id: A,
                            key: 'A',
                            isMeta: false,
                            modifier: undefined,
                        },
                    ],
                },
                'keystroke',
            );
            done();
        }, 0);
    };

    // FIXME: These tests create hanging timeouts.
    it.skip('send key with modifier - macos', ctrlTest(MAC_OS_KEY, 'Mac'));
    it.skip('send key with modifier - other', ctrlTest(OTHER_OS_KEY, 'other'));

    it('invalid event', () => {
        keyStrokeCaptor = new KeyStrokeCaptor(win, recorder, 'a');
        keyStrokeCaptor.start();

        const input = focus('input', 'password', 'ym-disable-keys');
        recorder.test.createEvent('keydown', {
            keyCode: LEFT_ARROW,
            target: input,
        });
        recorder.test.createEvent('keyup', {
            keyCode: LEFT_ARROW,
            target: input,
        });

        focus('object', 'flash');
        recorder.test.createEvent('keydown', {
            keyCode: LEFT_ARROW,
            target: input,
        });
        recorder.test.createEvent('keyup', {
            keyCode: LEFT_ARROW,
            target: input,
        });

        recorder.test.checkNoEvent();
    });

    it('keyup modifier', (done) => {
        keyStrokeCaptor = new KeyStrokeCaptor(win, recorder, 'a');
        keyStrokeCaptor.start();

        const input = focus('input');

        recorder.test.createEvent('keydown', { keyCode: CTRL, target: input });
        recorder.test.createEvent('keyup', { keyCode: CTRL, target: input });
        recorder.test.createEvent('keydown', { keyCode: A, target: input });
        setTimeout(() => {
            recorder.test.createEvent('keyup', { keyCode: A, target: input });
            recorder.test.checkNoEvent();
            done();
        }, 0);
    });

    it('ignore input with shift', () => {
        keyStrokeCaptor = new KeyStrokeCaptor(win, recorder, 'a');
        keyStrokeCaptor.start();

        const input = focus('input');

        recorder.test.createEvent('keydown', {
            keyCode: LEFT_ARROW,
            shiftKey: true,
            target: input,
        });
        recorder.test.createEvent('keyup', {
            keyCode: LEFT_ARROW,
            shiftKey: true,
            target: input,
        });
        recorder.test.checkNoEvent();
    });

    it('repeat key', () => {
        keyStrokeCaptor = new KeyStrokeCaptor(win, recorder, 'a');
        keyStrokeCaptor.start();

        const input = focus('input');
        recorder.test.createEvent('keydown', {
            keyCode: LEFT_ARROW,
            target: input,
        });
        recorder.test.createEvent('keydown', {
            keyCode: LEFT_ARROW,
            target: input,
            repeat: true,
        });
        recorder.test.createEvent('keyup', {
            keyCode: LEFT_ARROW,
            target: input,
        });

        sinon.assert.calledOnce(recorder.test.sendEventObjectSpy);
    });
});
