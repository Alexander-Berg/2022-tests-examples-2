import {
    CHANGE_PERSONAL_INFO,
    SET_PERSONAL_INFO_PROGRESS_STATE,
    SET_PERSONAL_INFO_ERRORS,
    SET_PERSONAL_INFO_UPDATE_STATUS,
    CLEAR_PERSONAL_INFO_FIELD_ERRORS,
    CLEAR_PERSONAL_INFO_FIELDS_ERRORS,
    UPDATE_MAIN_AVATAR
} from '../actions';
import {GLOBAL_FORM_ERRORS} from '../';

import reducer from '../reducers';

const state = {
    progress: false,
    updated: true,
    errors: {
        some: 'ERROR',
        [GLOBAL_FORM_ERRORS]: 'ERROR'
    }
};

describe('Morda.PersonalInfo.reducers', () => {
    it('should return default state', () => {
        expect(reducer()).toEqual({});
    });
    test(CHANGE_PERSONAL_INFO, () => {
        const action = {
            type: CHANGE_PERSONAL_INFO,
            props: {
                some: 'prop'
            }
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, action.props, {
                progress: false,
                updated: true,
                errors: {}
            })
        );
    });
    test(SET_PERSONAL_INFO_PROGRESS_STATE, () => {
        const action = {
            type: SET_PERSONAL_INFO_PROGRESS_STATE,
            progress: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                progress: action.progress,
                updated: false,
                errors: {}
            })
        );
    });
    test(SET_PERSONAL_INFO_ERRORS, () => {
        const action = {
            type: SET_PERSONAL_INFO_ERRORS,
            errors: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                progress: false,
                updated: false,
                errors: action.errors
            })
        );
    });
    test(SET_PERSONAL_INFO_UPDATE_STATUS, () => {
        const action = {
            type: SET_PERSONAL_INFO_UPDATE_STATUS,
            updated: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                updated: action.updated
            })
        );
    });
    test(CLEAR_PERSONAL_INFO_FIELD_ERRORS, () => {
        const action = {
            type: CLEAR_PERSONAL_INFO_FIELD_ERRORS,
            field: 'some'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                errors: {}
            })
        );
    });
    test(CLEAR_PERSONAL_INFO_FIELDS_ERRORS, () => {
        const action = {
            type: CLEAR_PERSONAL_INFO_FIELDS_ERRORS
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                errors: {}
            })
        );
    });
    test(UPDATE_MAIN_AVATAR, () => {
        const action = {
            type: UPDATE_MAIN_AVATAR,
            avatarId: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                avatarId: action.avatarId
            })
        );
    });
});
