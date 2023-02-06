import mobileMenuReducer from '../mobileMenu';

describe('Reducers: mobileMenu', () => {
    it('should handle CHANGE_MOBILE_MENU_VISIBILITY action', () => {
        const state = {};
        const action = {
            type: 'CHANGE_MOBILE_MENU_VISIBILITY',
            visible: false
        };

        const result = mobileMenuReducer(state, action);

        expect(result).toEqual({
            isShowMobileMenu: false,
            mobileMenuType: null
        });
    });

    it('should handle CHANGE_MOBILE_MENU_VISIBILITY action', () => {
        const state = {
            mobileMenuType: 'mobileMenuType'
        };
        const action = {
            type: 'CHANGE_MOBILE_MENU_VISIBILITY',
            visible: true
        };

        const result = mobileMenuReducer(state, action);

        expect(result).toEqual({
            isShowMobileMenu: true,
            mobileMenuType: 'mobileMenuType'
        });
    });

    it('should handle CHANGE_MOBILE_MENU_TYPE action', () => {
        const state = {};
        const action = {
            type: 'CHANGE_MOBILE_MENU_TYPE',
            mobileMenuType: 'mobileMenuType'
        };

        const result = mobileMenuReducer(state, action);

        expect(result).toEqual({
            mobileMenuType: 'mobileMenuType'
        });
    });

    it('should handle SET_PROCESSED_ACCOUNT_UID action', () => {
        const state = {};
        const action = {
            type: 'SET_PROCESSED_ACCOUNT_UID',
            processedAccountUid: 'processedAccountUid'
        };

        const result = mobileMenuReducer(state, action);

        expect(result).toEqual({
            processedAccountUid: 'processedAccountUid'
        });
    });

    it('should handle empty state and handle unknown action', () => {
        const action = {
            type: 'SAME_ACTION'
        };

        const result = mobileMenuReducer(undefined, action);

        expect(result).toEqual({});
    });
});
