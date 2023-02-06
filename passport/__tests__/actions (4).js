import {
    UPDATE_AVATAR,
    SET_AVATAR_STATUS,
    SET_AVATAR_ERROR,
    UPDATE_IMAGE_OPTIONS,
    updateAvatar,
    setAvatarError,
    updateAvatarStatus,
    updateImageOptions
} from '../';

describe('Morda.Avatar.actions', () => {
    test('updateAvatar', () => {
        const data = 'value';

        expect(updateAvatar(data)).toEqual({
            type: UPDATE_AVATAR,
            data
        });
    });
    test('setAvatarError', () => {
        const error = 'value';

        expect(setAvatarError(error)).toEqual({
            type: SET_AVATAR_ERROR,
            error
        });
    });
    test('setAvatarStatus', () => {
        const status = 'loading';

        expect(updateAvatarStatus(status)).toEqual({
            type: SET_AVATAR_STATUS,
            status: 'loading'
        });
    });
    test('updateImageOptions', () => {
        expect(
            updateImageOptions({
                type: 'png',
                compression: 0.6
            })
        ).toEqual({
            type: UPDATE_IMAGE_OPTIONS,
            data: {
                type: 'png',
                compression: 0.6
            }
        });
    });
});
