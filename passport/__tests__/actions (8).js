import * as actions from '../actions';

describe('Morda.PersonalInfo.actions', () => {
    test('changePersonalInfo', () => {
        const props = 'value';

        expect(actions.changePersonalInfo(props)).toEqual({
            type: actions.CHANGE_PERSONAL_INFO,
            props
        });
    });
    test('setPersonalInfoProgressState', () => {
        const progress = 'value';

        expect(actions.setPersonalInfoProgressState(progress)).toEqual({
            type: actions.SET_PERSONAL_INFO_PROGRESS_STATE,
            progress
        });
    });
    test('setPersonalInfoErrors', () => {
        const errors = 'value';

        expect(actions.setPersonalInfoErrors(errors)).toEqual({
            type: actions.SET_PERSONAL_INFO_ERRORS,
            errors
        });
    });
    test('clearPersonalInfoFieldErrors', () => {
        const field = 'value';

        expect(actions.clearPersonalInfoFieldErrors(field)).toEqual({
            type: actions.CLEAR_PERSONAL_INFO_FIELD_ERRORS,
            field
        });
    });
    test('clearPersonalInfoFieldsErrors', () => {
        const field = 'value';

        expect(actions.clearPersonalInfoFieldsErrors(field)).toEqual({
            type: actions.CLEAR_PERSONAL_INFO_FIELDS_ERRORS,
            field
        });
    });
    test('setPersonalInfoUpdateStatus', () => {
        const updated = 'value';

        expect(actions.setPersonalInfoUpdateStatus(updated)).toEqual({
            type: actions.SET_PERSONAL_INFO_UPDATE_STATUS,
            updated
        });
    });
    test('updateMainAvatar', () => {
        const avatarId = 'value';

        expect(actions.updateMainAvatar(avatarId)).toEqual({
            type: actions.UPDATE_MAIN_AVATAR,
            avatarId
        });
    });
});
