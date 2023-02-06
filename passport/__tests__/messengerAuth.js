import messengerAuth from '../messengerAuth';

describe('Reducers: messengerAuth', () => {
    it('should handle AUTH_MESSENGER_SENT action', () => {
        const state = {};
        const action = {
            type: 'AUTH_MESSENGER_SENT',
            code: '1234'
        };

        const result = messengerAuth(state, action);

        expect(result).toEqual({
            isSent: true,
            code: '1234'
        });
    });

    it('should handle SET_AUTH_MESSENGER_ERROR action', () => {
        const state = {};
        const action = {
            type: 'SET_AUTH_MESSENGER_ERROR',
            error: 'bot_api.request_failed'
        };

        const result = messengerAuth(state, action);

        expect(result).toEqual({
            error: 'bot_api.request_failed'
        });
    });

    it('should handle AUTH_MAIL_CANCELLED action', () => {
        const state = {};
        const action = {
            type: 'AUTH_MAIL_CANCELLED',
            status: true
        };

        const result = messengerAuth(state, action);

        expect(result).toEqual({
            isCancelled: true
        });
    });

    it('should handle SET_AUTH_MAIL_ERROR action', () => {
        const state = {};
        const action = {
            type: 'SET_AUTH_MAIL_ERROR',
            error: 'rate.limit_exceeded'
        };

        const result = messengerAuth(state, action);

        expect(result).toEqual({
            error: 'rate.limit_exceeded'
        });
    });
});
