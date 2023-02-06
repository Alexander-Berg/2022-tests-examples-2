import {showHint, updateAppPasswordsStatus, SHOW_HINT, APP_PASSWORDS_ENABLED} from '../actions';

describe('Morda.Access.actions', () => {
    test('showHint', () => {
        const hint = 'hint';

        expect(showHint(hint)).toEqual({
            type: SHOW_HINT,
            hint
        });
    });
    test('updateAppPasswordsStatus', () => {
        const enabled = true;

        expect(updateAppPasswordsStatus(enabled)).toEqual({
            type: APP_PASSWORDS_ENABLED,
            enabled
        });
    });
});
