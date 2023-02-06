import {castError} from './errors';

describe('utils/errors', () => {
    describe('castError', () => {
        it('error -> error', () => {
            const error = new Error();
            expect(castError(error)).toEqual(error);
        });

        it('string -> error', () => {
            expect(castError('error')).toBeInstanceOf(Error);
            expect(castError('error').message).toEqual('error');
        });

        it('any -> unknown error', () => {
            expect(castError({})).toBeInstanceOf(Error);
            expect(castError({}).message).toEqual('Unknown');
        });
    });
});
