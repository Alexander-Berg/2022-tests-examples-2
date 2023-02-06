import pagePopupReducer from '../pagePopup';

describe('Reducers: pagePopup', () => {
    it('should handle CHANGE_PAGE_POPUP_VISIBILITY action', () => {
        const state = {};
        const action = {
            type: 'CHANGE_PAGE_POPUP_VISIBILITY',
            visible: false
        };

        const result = pagePopupReducer(state, action);

        expect(result).toEqual({
            isShowPagePopup: false,
            pagePopupType: null
        });
    });

    it('should handle CHANGE_PAGE_POPUP_VISIBILITY action', () => {
        const state = {
            pagePopupType: 'pagePopupType'
        };
        const action = {
            type: 'CHANGE_PAGE_POPUP_VISIBILITY',
            visible: true
        };

        const result = pagePopupReducer(state, action);

        expect(result).toEqual({
            isShowPagePopup: true,
            pagePopupType: 'pagePopupType'
        });
    });

    it('should handle CHANGE_PAGE_POPUP_TYPE action', () => {
        const state = {};
        const action = {
            type: 'CHANGE_PAGE_POPUP_TYPE',
            pagePopupType: 'pagePopupType'
        };

        const result = pagePopupReducer(state, action);

        expect(result).toEqual({
            pagePopupType: 'pagePopupType'
        });
    });

    it('should handle empty state and handle unknown action', () => {
        const action = {
            type: 'SAME_ACTION'
        };

        const result = pagePopupReducer(undefined, action);

        expect(result).toEqual({});
    });
});
