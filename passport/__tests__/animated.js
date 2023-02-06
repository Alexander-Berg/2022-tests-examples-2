import * as extracted from '../animated.js';

jest.useFakeTimers();

describe('Dashboard.Animated', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            state: {},
            props: {},
            refs: {
                content: {
                    clientHeight: 0
                }
            }
        };
        obj.setState = jest.fn((any) => {
            obj.state = Object.assign({}, obj.state, typeof any === 'function' ? any(obj.state) : any);
        });
    });

    describe('recomputeHeight', () => {
        it('shouldnt call setState', () => {
            obj.refs.content.offsetHeight = 0;
            obj.auto = true;
            extracted.recomputeHeight.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(0);
            obj.props.forceHeight = 1;
            extracted.recomputeHeight.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(0);
            delete obj.props.forceHeight;
            obj.auto = false;
            extracted.recomputeHeight.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(0);
            obj.props.children = true;
            extracted.recomputeHeight.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(0);
            obj.refs.content.offsetHeight = obj.lastHeight = 123;
            extracted.recomputeHeight.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(0);
        });
        it('should call setState with contentHeight of 0', () => {
            obj.state.contentHeight = 123;
            extracted.recomputeHeight.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({contentHeight: 0});
            expect(obj.state.contentHeight).toBe(0);
        });
        it('should call setState with contentHeight of "auto" and set self auto to true', () => {
            obj.props.children = true;
            delete obj.refs.content.clientHeight;
            extracted.recomputeHeight.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({contentHeight: 'auto'});
            expect(obj.state.contentHeight).toBe('auto');
            expect(obj.auto).toBeTruthy();
        });
        it('should call setState, set self lastHeight, auto and timer, and call clearTimeout and setTimeout', () => {
            const clearTimeout = jest.spyOn(global, 'clearTimeout');
            const setTimeout = jest.spyOn(global, 'setTimeout');

            obj.props.children = true;
            obj.refs.content.clientHeight = 123;
            extracted.recomputeHeight.call(obj);
            expect(clearTimeout).toHaveBeenCalledTimes(1);
            expect(setTimeout).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({contentHeight: 123});
            expect(obj.state.contentHeight).toBe(123);
            jest.runAllTimers();
            expect(obj.setState).toHaveBeenCalledTimes(2);
            expect(obj.lastHeight).toBe(123);
            expect(obj.state.contentHeight).toBe('auto');

            clearTimeout.mockReset();
            setTimeout.mockReset();
        });
    });
});
