import access from '../reducers';
import {SHOW_HINT, APP_PASSWORDS_ENABLED} from '../actions';

describe('Morda.Access.reducers', () => {
    const state = {
        featureHint: null,
        isAppPasswordsEnabled: false
    };

    describe('access', () => {
        it('should change featureHint', () => {
            const hint = 'hint';

            expect(
                access(state, {
                    type: SHOW_HINT,
                    hint
                })
            ).toEqual(
                Object.assign({}, state, {
                    featureHint: hint
                })
            );
        });
        it('should change isAppPasswordsEnabled', () => {
            const enabled = true;

            expect(
                access(state, {
                    type: APP_PASSWORDS_ENABLED,
                    enabled
                })
            ).toEqual(
                Object.assign({}, state, {
                    isAppPasswordsEnabled: enabled
                })
            );
        });
        it('should return empty object', () => {
            expect(access(undefined, {})).toEqual({});
        });
    });
});
