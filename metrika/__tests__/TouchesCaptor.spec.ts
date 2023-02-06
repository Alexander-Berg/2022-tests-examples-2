import chai from 'chai';
import * as utils from '@src/utils/guid';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';
import { SCROLL_TIMEOUT, TouchesCaptor } from '../TouchesCaptor';
import {
    createRecorderMock,
    STAMP,
} from '../../AbstractCaptor/__tests__/createMockRecorder';

describe('TouchesCaptor', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const UID = '132';
    const X = 10;
    const Y = 20;
    const win: any = {
        setTimeout: window.setTimeout.bind(window),
        clearTimeout: window.clearTimeout.bind(window),
    };
    let recorder: any;
    let touchesCaptor: any;

    beforeEach(() => {
        recorder = createRecorderMock();
        recorder.test.sandbox.stub(utils, 'getGuid').returns(UID);

        touchesCaptor = new TouchesCaptor(win, recorder, 'a');
        touchesCaptor.start();
    });

    afterEach(() => {
        recorder.test.restore();
        touchesCaptor.stop();
    });

    it('TouchesCaptor - throttleManager usage', () => {
        recorder.test.checkThrottleManagerUsage(win);
    });

    it('touchstart', () => {
        const target = document.createElement('div');
        recorder.test.createEvent('touchstart', {
            type: 'touchstart',
            target,
            changedTouches: [
                {
                    identifier: 1,
                    clientX: X,
                    clientY: Y,
                    force: false,
                },
            ],
        });
        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                touches: [
                    {
                        id: UID,
                        x: X,
                        y: Y,
                        force: false,
                    },
                ],
                target,
            },
            'touchstart',
            0,
            STAMP,
        );
    });

    it('touchmove without scroll', () => {
        const target = document.createElement('div');
        recorder.test.createEvent('touchmove', {
            type: 'touchmove',
            target,
            changedTouches: [
                {
                    identifier: 1,
                    clientX: X,
                    clientY: Y,
                    force: false,
                },
            ],
        });
        recorder.test.checkCallThrottledHandler();
        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                touches: [
                    {
                        id: UID,
                        x: X,
                        y: Y,
                        force: false,
                    },
                ],
                target,
            },
            'touchmove',
            0,
            STAMP,
        );
    });
    it('touchmove with scroll', (done) => {
        const changedTouchItem = {
            identifier: 1,
            clientX: X,
            clientY: Y,
            force: false,
        };
        const touchItemToCheck = {
            id: UID,
            x: X,
            y: Y,
            force: false,
        };
        const target = document.createElement('div');
        recorder.test.createEvent('scroll', {});
        recorder.test.createEvent('touchmove', {
            type: 'touchmove',
            target,
            changedTouches: [changedTouchItem],
        });
        recorder.test.checkCallOriginalHandler();
        recorder.test.checkSendEvent(
            EVENT_EVENT_TYPE,
            {
                touches: [touchItemToCheck],
                target,
            },
            'touchmove',
            0,
            STAMP,
        );

        setTimeout(() => {
            recorder.test.createEvent('touchmove', {
                type: 'touchmove',
                target,
                changedTouches: [changedTouchItem],
            });
            recorder.test.checkCallThrottledHandler();
            recorder.test.checkSendEvent(
                EVENT_EVENT_TYPE,
                {
                    touches: [touchItemToCheck],
                    target,
                },
                'touchmove',
                0,
                STAMP,
            );
            done();
        }, SCROLL_TIMEOUT + 1);
    });
    it('clear touchIdsMap', () => {
        const target = document.createElement('div');
        const touch = {
            identifier: 1,
            clientX: X,
            clientY: Y,
            force: false,
        };
        recorder.test.createEvent('touchmove', {
            type: 'touchmove',
            target,
            changedTouches: [touch],
        });
        chai.expect(touchesCaptor.touchIdsMap).to.have.property('1');
        recorder.test.createEvent('touchend', {
            type: 'touchend',
            target,
            changedTouches: [touch],
        });
        chai.expect(touchesCaptor.touchIdsMap).to.not.have.property('1');
    });
});
