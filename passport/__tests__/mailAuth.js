import mailAuthReducer from '../mailAuth';

describe('Reducers: mailAuth', () => {
    it('should handle AUTH_MAIL_SENT action', () => {
        const state = {};
        const action = {
            type: 'AUTH_MAIL_SENT'
        };

        const result = mailAuthReducer(state, action);

        expect(result).toEqual({
            isAuthMailSent: true
        });
    });

    it('should handle AUTH_MAIL_CONFIRMED action', () => {
        const state = {};
        const action = {
            type: 'AUTH_MAIL_CONFIRMED'
        };

        const result = mailAuthReducer(state, action);

        expect(result).toEqual({
            isAuthConfirmed: true
        });
    });

    it('should handle AUTH_MAIL_CANCELLED action', () => {
        const state = {};
        const action = {
            type: 'AUTH_MAIL_CANCELLED',
            status: true
        };

        const result = mailAuthReducer(state, action);

        expect(result).toEqual({
            isAuthCancelled: true
        });
    });

    it('should handle TOGGLE_MAIL_SENT_TOOLTIP action', () => {
        const state = {};

        let action = {
            type: 'TOGGLE_MAIL_SENT_TOOLTIP',
            isVisible: false
        };

        let result = mailAuthReducer(state, action);

        expect(result).toEqual({
            isAuthMailConfirmationVisible: false
        });

        action = {
            type: 'TOGGLE_MAIL_SENT_TOOLTIP',
            isVisible: true
        };

        result = mailAuthReducer(state, action);

        expect(result).toEqual({
            isAuthMailConfirmationVisible: true
        });
    });

    it('should handle SET_AUTH_MAIL_ERROR action', () => {
        const state = {};
        const action = {
            type: 'SET_AUTH_MAIL_ERROR',
            error: 'error.1'
        };

        const result = mailAuthReducer(state, action);

        expect(result).toEqual({
            mailAuthError: 'error.1'
        });
    });

    it('should handle SET_AUTH_MAIL_UPDATED action', () => {
        const state = {};
        const action = {
            type: 'SET_AUTH_MAIL_UPDATED',
            isUpdated: true
        };

        const result = mailAuthReducer(state, action);

        expect(result).toEqual({
            isUpdatedAuthLetterStatus: true
        });
    });

    it('should handle SET_AUTH_MAIL_DISABLED action', () => {
        const state = {};
        const action = {
            type: 'SET_AUTH_MAIL_DISABLED'
        };

        const result = mailAuthReducer(state, action);

        expect(result).toEqual({
            isEnabled: false
        });
    });

    it('should handle UPDATE_LOGIN_VALUE action', () => {
        const state = {};
        const action = {
            type: 'UPDATE_LOGIN_VALUE'
        };

        const result = mailAuthReducer(state, action);

        expect(result).toEqual({
            isAuthCancelled: false,
            isAuthMailSent: false,
            isAuthConfirmed: false,
            isAuthMailConfirmationVisible: false,
            mailAuthError: '',
            isUpdatedAuthLetterStatus: false
        });
    });

    it('should fallback on default state and handle unknown action', () => {
        const action = {
            type: 'SAME_ACTION'
        };
        const result = mailAuthReducer(undefined, action);

        expect(result).toEqual({});
    });
});
