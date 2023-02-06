import api from '../../../../api';

import {updateAvatar, setAvatarError, updateAvatarStatus} from '../';
import loadAvatarByUrl from '../loadAvatarByUrl';
import {avatarCropper} from '../../helpers/avatarCropper';
import forceClearFileInput from '../../helpers/forceClearFileInput';
import handleErrorsFromLoadByUrl from '../../helpers/handleErrorsFromLoadByUrl';

jest.mock('../../../../api');

jest.mock('../', () => ({
    updateAvatar: jest.fn(),
    setAvatarError: jest.fn(),
    updateAvatarStatus: jest.fn()
}));

jest.mock('../../helpers/avatarCropper');

jest.mock('../../helpers/forceClearFileInput');
jest.mock('../../helpers/handleErrorsFromLoadByUrl');

const dispatch = jest.fn();
const getState = jest.fn(() => ({
    person: {avatarId: '0-0'},
    changeAvatar: {
        defaultSize: 'islands-300',
        defaultUrl: '/get-yapic/0/0-0/islands-300',
        track_id: '2345'
    },
    common: {
        csrf: '7897cj'
    },
    settings: {
        avatar: {
            avatar_300: '/get-yapic/%avatar_id%/islands-300'
        },
        location: '/profile/'
    }
}));

describe('avatars: loadAvatarByUrl', () => {
    afterEach(() => {
        api.request.mockClear();
        setAvatarError.mockClear();
    });

    it('should call some set-up functions', () => {
        loadAvatarByUrl('some-url')(dispatch, getState);
        expect(avatarCropper.destroyCropper).toBeCalled();
        expect(forceClearFileInput).toBeCalled();
        expect(setAvatarError).toBeCalled();
        expect(updateAvatar).toBeCalledWith({
            isByUrl: true
        });
        expect(updateAvatarStatus).toBeCalledWith('loading');
    });

    it('should dispatch setAvatarError with error "error-url.empty" if url is not passed', () => {
        loadAvatarByUrl()(dispatch, getState);
        expect(setAvatarError).toBeCalledWith('error-url.empty');
    });

    describe('loadAvatarByUrl: request succeed', () => {
        beforeEach(() => {
            api.__mockSuccess({
                body: {
                    status: 'ok',
                    avatar_url: 'some-url'
                }
            });
            updateAvatar.mockClear();
        });

        it('should dispatch updateAvatar with proper params', () => {
            loadAvatarByUrl('some-url')(dispatch, getState);
            expect(updateAvatar).toBeCalledWith({
                avatarUrl: '/profile/avatars/image?path=https://some-urlislands-300',
                error: ''
            });
            expect(updateAvatarStatus).toBeCalledWith('processing');
        });

        it('should call avatarCroper.init method', () => {
            loadAvatarByUrl('some-url')(dispatch, getState);
            expect(avatarCropper.init).toBeCalled();
        });
    });

    describe('loadAvatarByUrl: something went wrong', () => {
        beforeEach(() => {
            api.__mockSuccess(['change_avatar.invalid_yapic_response']);
            updateAvatar.mockClear();
        });

        it('should call handleErrorsFromLoadByUrl', () => {
            loadAvatarByUrl('some-url')(dispatch, getState);
            expect(handleErrorsFromLoadByUrl).toBeCalled();
        });
    });
});
