import metrics from '../../../../metrics';

import * as extracted from '../scroll.js';

jest.mock('lodash/debounce', () => (event) => event);
jest.mock('../../../../common/event_listeners', () => jest.fn((type, method) => ({type, method})));
jest.mock('../../../../metrics', () => ({
    send: jest.fn()
}));

describe('Morda.Scroll', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            scroll: jest.fn(),
            forceUpdate: jest.fn(),
            setState: jest.fn(),
            cardsInfo: {
                count: 2,
                width: 100
            },
            sizes: [
                {
                    maxWidth: 100,
                    cardCount: 2,
                    cardWidth: 150
                }
            ],
            scrolled: 2,
            scrollRef: {
                current: {
                    clientWidth: 200
                }
            },
            props: {
                items: [1, 2, 3, 4],
                fixed: false,
                marginRight: 0,
                sizes: [],
                metrics: [],
                isTouch: false
            }
        };
    });
    describe('construct', () => {
        it('should sort sizes', () => {
            obj.props.sizes = [
                {
                    maxWidth: 100
                },
                {
                    maxWidth: 200
                }
            ];

            extracted.construct.call(obj, obj.props);
            expect(obj.sizes).toEqual([
                {
                    maxWidth: 200
                },
                {
                    maxWidth: 100
                }
            ]);
        });
        it('should return same sizes', () => {
            extracted.construct.call(obj, obj.props);
            expect(obj.sizes === obj.props.sizes).toBeTruthy();
        });
        it('should set sendMetrics property', () => {
            obj.props.metrics = [1, 2];

            extracted.construct.call(obj, obj.props);
            expect(obj.sendMetrics).not.toBe(undefined);
        });
        it('shouldnt set sendMetrics property', () => {
            extracted.construct.call(obj, obj.props);
            expect(obj.sendMetrics).toBe(undefined);
        });
    });
    describe('sendMetrics', () => {
        it('should send metrics', () => {
            const mData = ['header', 'msg'];

            extracted.sendMetrics.call(obj, mData[0], mData[1]);
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(mData);
        });
    });
    describe('onScroll', () => {
        test('if not fixed and direction is left', () => {
            extracted.onScroll.call(obj, 'left');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                scroll: 0
            });
        });
        test('if not fixed and direction is right', () => {
            extracted.onScroll.call(obj, 'right');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                scroll: 200
            });
        });
        test('if fixed and direction is left', () => {
            obj.props.fixed = true;

            extracted.onScroll.call(obj, 'left');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                scroll: 0
            });
        });
        test('if fixed and direction is right', () => {
            obj.props.fixed = true;

            extracted.onScroll.call(obj, 'right');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                scroll: 200
            });
        });
        test('if no direction', () => {
            obj.props.fixed = true;

            extracted.onScroll.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                scroll: 200
            });
        });
    });
    describe('listenForResize', () => {
        it('should listen for resize and call method scroll', () => {
            extracted.listenForResize.call(obj);
            obj.destroyListener.method();
            expect(obj.destroyListener.type).toBe('resize');
            expect(obj.scroll).toHaveBeenCalledTimes(1);
        });
    });
    describe('updateAsyncIfNotFixed', () => {
        it('should call forceUpdate', () => {
            obj.props.fixed = obj.props.isTouch = true;

            jest.useFakeTimers();
            extracted.updateAsyncIfNotFixed.call(obj);
            jest.runAllTimers();
            expect(obj.forceUpdate).toHaveBeenCalledTimes(1);
        });
    });
    describe('getCardsInfo', () => {
        test('if fixed', () => {
            obj.props.fixed = true;
            window.innerWidth = 0;
            global.document = {
                body: {
                    clientWidth: 1000
                }
            };

            expect(extracted.getCardsInfo.call(obj)).toEqual({
                width: 150,
                count: 2
            });
        });
        test('if fixed', () => {
            window.innerWidth = 0;
            global.document = {
                documentElement: {
                    clientWidth: 1000
                }
            };

            expect(extracted.getCardsInfo.call(obj)).toEqual({
                width: 150,
                count: 2
            });
        });
        it('should fallback to last size', () => {
            const last = obj.sizes[obj.sizes.length - 1];

            window.innerWidth = 1000;
            last.maxWidth = 1001;

            expect(extracted.getCardsInfo.call(obj)).toEqual({
                width: last.cardWidth,
                count: last.cardCount
            });
        });
    });
});
