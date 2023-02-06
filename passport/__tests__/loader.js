import * as extracted from '../loader.js';

jest.useFakeTimers();

describe('Dashboard.Loader', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {},
            forceUpdate: jest.fn()
        };
    });

    describe('update', () => {
        it('shouldnt set self timer or remove', () => {
            obj.timer = 123;
            extracted.update.call(obj);
            expect(obj.timer).toBe(123);
            expect(obj.remove).toBe(undefined);
        });
        it('should set self timer to null and call clearTimeout', () => {
            const clearTimeout = jest.spyOn(global, 'clearTimeout');

            obj.props.isLoading = true;
            obj.timer = true;
            extracted.update.call(obj);
            expect(obj.timer).toBe(null);
            expect(clearTimeout).toHaveBeenCalledTimes(1);
            expect(clearTimeout).toHaveBeenCalledWith(true);

            clearTimeout.mockReset();
        });
        it('should set self removed to false', () => {
            obj.props.isLoading = true;
            extracted.update.call(obj);
            expect(obj.removed).toBe(false);
        });
        it('should call setTimeout and self forceUpdate, and self set timer to null and removed to true', () => {
            const setTimeout = jest.spyOn(global, 'setTimeout');

            extracted.update.call(obj);
            jest.runAllTimers();
            expect(setTimeout).toHaveBeenCalledTimes(1);
            expect(obj.forceUpdate).toHaveBeenCalledTimes(1);
            expect(obj.timer).toBe(null);
            expect(obj.removed).toBe(true);

            setTimeout.mockReset();
        });
    });
});
