import metrics from '@blocks/metrics';

import * as extracted from '../scroll.js';

jest.mock('@blocks/metrics', () => ({
    send: jest.fn()
}));

global.window = {
    innerWidth: 1000
};

describe('Dashboard.Main.Scroll', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            state: {
                scroll: 0
            },
            props: {
                fade: true,
                cardCount: 3,
                items: [1, 2, 3, 4, 5, 6, 7, 8]
            }
        };
    });
    describe('onScroll', () => {
        test('if direction is "left"', () => {
            obj.setState = jest.fn((method) => {
                expect(
                    method({
                        scroll: 5
                    })
                ).toEqual({
                    scroll: 2
                });
            });

            extracted.onScroll.call(obj, 'left');
        });
        test('if direction is "right"', () => {
            obj.setState = jest.fn((method) => {
                expect(
                    method({
                        scroll: 0
                    })
                ).toEqual({
                    scroll: 3
                });
            });

            extracted.onScroll.call(obj, 'right');
        });
    });
    describe('getMax', () => {
        it('should return 5', () => {
            obj.cardCount = 3;

            expect(extracted.getMax.call(obj)).toBe(5);
        });
        it('should return 6', () => {
            obj.cardCount = 3;
            obj.props.link = 'link';

            expect(extracted.getMax.call(obj)).toBe(6);
        });
        it('should return 0', () => {
            obj.cardCount = 20;

            expect(extracted.getMax.call(obj)).toBe(0);
        });
    });
    describe('updateCardCount', () => {
        it('should set cardCount to 3', () => {
            global.window.innerWidth = 123000;

            extracted.updateCardCount.call(obj);
            expect(obj.cardCount).toBe(obj.props.cardCount);
        });
        it('should set cardCount to 2', () => {
            global.window.innerWidth = 800;

            extracted.updateCardCount.call(obj);
            expect(obj.cardCount).toBe(2);
        });
    });
    describe('construct', () => {
        it('should set false to sendMetrics', () => {
            extracted.construct.call(obj, {});
            expect(obj.sendMetrics).toBeFalsy();
            extracted.construct.call(obj, {metrics: []});
            expect(obj.sendMetrics).toBeFalsy();
        });
        it('should set method to sendMetrics', () => {
            const mData = {metrics: [1, 2]};

            extracted.construct.call(obj, mData);
            expect(typeof obj.sendMetrics).toBe('function');
            obj.sendMetrics();
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(mData.metrics);
        });
    });
    describe('updateScroll', () => {
        it('should call forceUpdate', () => {
            obj.forceUpdate = jest.fn();
            extracted.updateScroll.call(obj);
            expect(obj.forceUpdate).toHaveBeenCalledTimes(1);
        });
        it('should not call forceUpdate', () => {
            obj.cardCount = 3;
            obj.forceUpdate = jest.fn();
            global.window.innerWidth = 123000;

            extracted.updateScroll.call(obj);
            expect(obj.forceUpdate).toHaveBeenCalledTimes(0);
        });
    });
});
