import api from '../../../../api';

import {updateAvatar, setAvatarError, updateAvatarStatus} from '../';
import getInitialAvatarsTrack from '../getInitialAvatarsTrack';

jest.mock('../../../../api');

jest.mock('../', () => ({
    updateAvatar: jest.fn(),
    setAvatarError: jest.fn(),
    updateAvatarStatus: jest.fn()
}));

const dispatch = jest.fn();
const getState = jest.fn(() => ({
    person: {avatarId: '0-0'},
    changeAvatar: {
        defaultSize: 'islands-300',
        defaultUrl: '/get-yapic/0/0-0/islands-300',
        queryUid: undefined
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

describe('avatars: setInitialAvatarData', () => {
    afterEach(() => {
        api.request.mockClear();
    });

    it('should normalize process status', () => {
        getInitialAvatarsTrack()(dispatch, getState);
        expect(updateAvatarStatus).toBeCalledWith('normal');
    });

    describe('setInitialAvatarData: request succeed', () => {
        beforeEach(() => {
            api.__mockSuccess({status: 'ok', avatars: [{}]});
        });

        it('should dispatch updateAvatar with proper params', () => {
            getInitialAvatarsTrack()(dispatch, getState);
            expect(updateAvatar).toBeCalledWith({
                avatarUrl: '/get-yapic/0-0/islands-300',
                isDeletePossible: true
            });
        });
    });

    describe('setInitialAvatarData: request not succeed', () => {
        beforeEach(() => {
            api.__mockFail({error: ['change_avatar.invalid_yapic_response']});
        });

        it('should dispatch setAvatarError when something went wrong', () => {
            getInitialAvatarsTrack()(dispatch, getState);
            expect(setAvatarError).toBeCalled();
        });
    });
});
