import timeout from '../timeout';

describe('utils:timeout', () => {
    beforeAll(() => {
    });

    test('timeout должен возвращать промис', () => {
        expect(timeout(1)).toBeInstanceOf(Promise);
    });

    test('timeout должен резолвится спустя указанное время', () => {
        const cb = jest.fn();

        const timer = timeout(1).then(() => cb());

        expect(cb).not.toBeCalled();

        return timer.then(() => {
            expect(cb).toBeCalled();
        });
    });
});
