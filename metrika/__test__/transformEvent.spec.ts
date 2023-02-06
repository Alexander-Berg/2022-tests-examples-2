import * as chai from 'chai';
import { transformEvent } from '../transformEvent';

describe('events transformer', () => {
    const defaultGroupEvents = [
        'touchmove',
        'touchstart',
        'touchend',
        'touchcancel',
        'touchforcechange',
        'scroll',
        'change',
        'mousemove',
        'mousedown',
        'mouseup',
        'click',
        'selection',
    ];
    const noMetaGroupEvents = ['windowfocus', 'windowblur', 'focus'];
    const unchangedMetaEvents = ['deviceRotation', 'resize'];

    it('transforms keystroke event', () => {
        const event = {
            type: 'event',
            event: 'keystroke',
            stamp: 100,
            frameId: 0,
            data: {
                keystrokes: ['data', 'data1'],
            },
        } as any;
        const result = transformEvent(event);
        chai.expect(result).to.be.deep.eq({
            type: 'event',
            stamp: 100,
            data: {
                frameId: 0,
                type: 'keystroke',
                meta: ['data', 'data1'],
            },
        });
    });

    it(`transforms ${unchangedMetaEvents}`, () => {
        unchangedMetaEvents.forEach((eventName) => {
            const event = {
                event: eventName,
                stamp: 100,
                frameId: 0,
                data: {
                    target: 123,
                    someData: 'data',
                },
            } as any;
            const result = transformEvent(event);
            chai.expect(result).to.be.deep.eq({
                type: 'event',
                stamp: 100,
                data: {
                    frameId: 0,
                    type: eventName,
                    meta: {
                        target: 123,
                        someData: 'data',
                    },
                },
            });
        });
    });

    it(`transforms ${noMetaGroupEvents.join(', ')}`, () => {
        noMetaGroupEvents.forEach((eventName) => {
            const event = {
                event: eventName,
                stamp: 100,
                frameId: 0,
                data: {
                    target: 123,
                },
            } as any;
            const result = transformEvent(event);
            chai.expect(result).to.be.deep.eq({
                type: 'event',
                stamp: 100,
                data: {
                    target: 123,
                    frameId: 0,
                    type: eventName,
                    meta: null,
                },
            });
        });
    });

    it(`transforms ${defaultGroupEvents.join(', ')}`, () => {
        defaultGroupEvents.forEach((eventName) => {
            const event = {
                event: eventName,
                stamp: 100,
                frameId: 0,
                data: {
                    target: 123,
                    someData: 'data',
                },
            } as any;
            const result = transformEvent(event);
            chai.expect(result).to.be.deep.eq({
                type: 'event',
                stamp: 100,
                data: {
                    target: 123,
                    frameId: 0,
                    type: eventName,
                    meta: {
                        someData: 'data',
                    },
                },
            });
        });
    });

    it('transforms zoom event', () => {
        const event = {
            event: 'zoom',
            frameId: 0,
            stamp: 100,
            data: {
                x: 100,
                y: 100,
                level: 2,
            },
        } as any;
        const result = transformEvent(event);

        chai.expect(result).to.be.deep.eq({
            type: 'event',
            stamp: 100,
            data: {
                type: 'zoom',
                frameId: 0,
                meta: {
                    zoomFrom: {
                        x: 0,
                        y: 0,
                        level: 0,
                    },
                    zoomTo: {
                        x: 100,
                        y: 100,
                        level: 2,
                    },
                    duration: 1,
                },
            },
        });
    });

    it('transforms srcset event', () => {
        const event = {
            event: 'srcset',
            frameId: 0,
            stamp: 100,
            data: {
                value: 'some-src',
                target: 123,
            },
        } as any;
        const result = transformEvent(event);

        chai.expect(result).to.be.deep.eq({
            type: 'mutation',
            stamp: 100,
            data: {
                frameId: 0,
                meta: {
                    changes: [
                        {
                            c: [
                                {
                                    id: 123,
                                    at: {
                                        src: {
                                            o: '',
                                            n: 'some-src',
                                            r: false,
                                        },
                                    },
                                    i: 0,
                                },
                            ],
                        },
                    ],
                    index: 0,
                },
            },
        });
    });
});
