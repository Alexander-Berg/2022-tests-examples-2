import isPromise from '../isPromise';

describe('utils:isPromise', () => {
    test('isPromise возвращает true если передать промис', () => {
        expect(isPromise(Promise.resolve())).toBeTruthy();
    });

    test('isPromise возвращает false если передать не промис', () => {
        expect(isPromise({})).not.toBeTruthy();
    });
});
