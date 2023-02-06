import {
    updateTakeoutStatus,
    updateTakeoutData,
    togglePasswordVisibility,
    notifyPasswordCopied,
    updateLoadingStatus
} from '../';

describe('check takeout actions', () => {
    it('should return object with "UPDATE_TAKEOUT_STATUS key"', () => {
        const expected = {
            type: 'UPDATE_TAKEOUT_STATUS',
            status: 'isReady'
        };
        const result = updateTakeoutStatus('isReady');

        expect(expected).toEqual(result);
    });

    it('should return object with "UPDATE_TAKEOUT_DATA key"', () => {
        const expected = {
            type: 'UPDATE_TAKEOUT_DATA',
            data: {
                field: 'error',
                value: 'Что-то не так'
            }
        };
        const result = updateTakeoutData({field: 'error', value: 'Что-то не так'});

        expect(expected).toEqual(result);
    });

    it('should return object with "TOGGLE_PASSWORD_VISIBILITY"', () => {
        const expected = {
            type: 'TOGGLE_PASSWORD_VISIBILITY'
        };
        const result = togglePasswordVisibility();

        expect(expected).toEqual(result);
    });

    it('should return object with "NOTIFY_PASSWORD_COPIED"', () => {
        const expected = {
            type: 'NOTIFY_PASSWORD_COPIED'
        };
        const result = notifyPasswordCopied();

        expect(expected).toEqual(result);
    });

    it('should return object with "UPDATE_LOADING_STATUS"', () => {
        const expected = {
            type: 'UPDATE_LOADING_STATUS'
        };
        const result = updateLoadingStatus();

        expect(expected).toEqual(result);
    });
});
