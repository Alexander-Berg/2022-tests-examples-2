import {avatarCropper} from '../../helpers/avatarCropper';
import {updateAvatar, setAvatarError, updateAvatarStatus} from '../';

jest.mock('../', () => ({
    updateAvatar: jest.fn(),
    setAvatarError: jest.fn(),
    updateAvatarStatus: jest.fn()
}));

const dispatch = jest.fn();
const getState = jest.fn(() => ({
    person: {avatarId: '0-0'},
    changeAvatar: {
        isByUrl: false,
        status: 'processing',
        backupAvatar: {
            url: 'some-url'
        }
    }
}));

describe('destroyCropImage', () => {
    it('should call destroyCropper method from avatarCropper', () => {
        avatarCropper.destroyCropper = jest.fn();
        avatarCropper.destroyCropImage()(dispatch, getState);
        expect(avatarCropper.destroyCropper).toBeCalled();
    });

    it('should dispatch updateAvatar with proper arguments', () => {
        avatarCropper.updateAvatar = jest.fn();
        avatarCropper.updateAvatarStatus = jest.fn();
        avatarCropper.destroyCropImage()(dispatch, getState);
        expect(updateAvatar).toBeCalledWith({
            avatarUrl: 'some-url',
            isByUrl: false,
            loadUrlPath: '',
            hasChanged: false
        });
        expect(updateAvatarStatus).toBeCalledWith('normal');
    });

    it('should dispatch setAvatarError with proper arguments', () => {
        avatarCropper.setAvatarError = jest.fn();
        avatarCropper.destroyCropImage()(dispatch, getState);
        expect(setAvatarError).toBeCalledWith('');
    });

    it('should dispatch setAvatarError with proper arguments', () => {
        avatarCropper.setAvatarError = jest.fn();
        avatarCropper.destroyCropImage('error-file.size')(dispatch, getState);
        expect(setAvatarError).toBeCalledWith('error-file.size');
    });
});
