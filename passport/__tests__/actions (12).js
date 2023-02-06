import * as actions from '../actions';

describe('registration lite actions', () => {
    it('update email confirmation status', () => {
        const state = true;

        expect(actions.updateEmailConfirmationStatus(true)).toEqual({
            type: actions.EMAIL_CONFIRMATION_DONE,
            state
        });
    });
});
