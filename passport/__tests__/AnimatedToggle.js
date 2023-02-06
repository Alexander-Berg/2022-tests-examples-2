import * as extracted from '../AnimatedToggle.js';

jest.useFakeTimers();

describe('Dashboard.Animated', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            state: {},
            props: {
                isOpened: true
            },
            content: {
                clientHeight: 123
            }
        };
        obj.setState = jest.fn((any) => {
            obj.state = Object.assign({}, obj.state, typeof any === 'function' ? any(obj.state) : any);
        });
    });

    describe('constructState', () => {
        it('should set contentHeight to 0', () => {
            extracted.constructState.call(obj, {isOpened: false});
            expect(obj.state.contentHeight).toBe(0);
        });
        it('should set contentHeight to "auto"', () => {
            extracted.constructState.call(obj, {isOpened: true});
            expect(obj.state.contentHeight).toBe('auto');
        });
    });

    describe('recomputeHeight', () => {
        it('should set contentHeight state to 0', () => {
            obj.content.offsetHeight = 123;

            extracted.recomputeHeight.call(obj, false);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.state.contentHeight).toBe(obj.content.offsetHeight);
            jest.runAllTimers();
            expect(obj.setState).toHaveBeenCalledTimes(2);
            expect(obj.state.contentHeight).toBe(0);
        });
        it('should set right contentHeght', () => {
            extracted.recomputeHeight.call(obj, true);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.state.contentHeight).toBe(123);
            expect(obj.timer).not.toBe(undefined);
            jest.runAllTimers();
            expect(obj.setState).toHaveBeenCalledTimes(2);
            expect(obj.state.contentHeight).toBe('auto');
        });
    });
});
