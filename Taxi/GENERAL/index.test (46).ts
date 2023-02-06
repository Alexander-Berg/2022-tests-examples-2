/* eslint-disable max-len */
import {
    BaseError,
    errorToJsonObject,
    errorToString,
    flattenError,
    I18nTemplate,
    instanceOfError,
    jsonObjectToError,
    OnRaise,
    stringToError
} from '.';

describe('package "error"', () => {
    it('should handle "I18nTemplate" decorator', () => {
        @I18nTemplate('Hello, {name}!')
        class AError extends BaseError {}

        expect(new AError().message).toEqual('Hello, {name}!');
        expect(new AError('Overridden i18n template').message).toEqual('Overridden i18n template');
    });

    it('should handle "onRaise" decorator', () => {
        const logs: string[] = [];
        const writeLog = function (this: BaseError) {
            logs.push(this.name);
        };

        @OnRaise(writeLog)
        class AError extends BaseError {}

        new AError();
        expect(logs).toEqual(['AError']);
    });

    it('should handle "errorToJsonObject" function', () => {
        class AError extends BaseError {}
        class BError extends BaseError {}
        class CError extends Error {}

        const err = new AError(new BError(new CError()));

        expect(errorToJsonObject(err)).toEqual({
            name: 'AError',
            message: '',
            cause: {
                name: 'BError',
                message: '',
                cause: {
                    name: 'CError',
                    message: ''
                }
            }
        });
    });

    it('should handle "errorToString" function', () => {
        class AError extends BaseError {}
        class BError extends BaseError {}
        class CError extends Error {}

        const err = new AError(new BError(new CError()));

        expect(errorToString(err)).toEqual(
            '{"name":"AError","message":"","cause":{"name":"BError","message":"","cause":{"name":"CError","message":""}}}'
        );
    });

    it('should handle "jsonObjectToError" function', () => {
        const errObj = {
            name: 'AError',
            message: 'AErrorMessage',
            meta: {foo: 'bar'},
            cause: {
                name: 'BError',
                message: 'BErrorMessage',
                meta: {baz: 'qux'},
                cause: {
                    name: 'CError',
                    message: 'CErrorMessage'
                }
            }
        };

        const err = jsonObjectToError(errObj);

        expect(errorToJsonObject(err)).toEqual(errObj);
    });

    it('should handle "stringToError" function', () => {
        const errStr =
            '{"name":"AError","message":"AErrorMessage","meta":{"foo":"bar"},"cause":{"name":"BError","message":"BErrorMessage","meta":{"baz":"qux"},"cause":{"name":"CError","message":"CErrorMessage"}}}';

        const err = stringToError(errStr);

        expect(errorToString(err)).toEqual(errStr);
    });

    it('should flatten error', () => {
        class AError extends BaseError {}
        class BError extends BaseError {}
        class CError extends Error {}

        const err = new AError(new BError(new CError()));

        expect(flattenError(err).map((e) => errorToJsonObject(e))).toEqual([
            {
                cause: {cause: {message: '', name: 'CError'}, message: '', meta: undefined, name: 'BError'},
                message: '',
                meta: undefined,
                name: 'AError'
            },
            {cause: {message: '', name: 'CError'}, message: '', meta: undefined, name: 'BError'},
            {message: '', name: 'CError'}
        ]);
    });

    it('should handle "instanceOfError" function', () => {
        class AError extends BaseError {}
        class BError extends BaseError {}
        class CError extends Error {}

        const err = new AError(new BError(new CError()));

        expect(instanceOfError(err, AError)).toBeTruthy();
        expect(instanceOfError(err, BError)).toBeTruthy();
        expect(instanceOfError(err, CError)).toBeTruthy();
    });
});
