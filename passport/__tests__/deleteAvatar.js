import api from '../../../../api';

import {updateAvatar, setAvatarError, updateAvatarStatus} from '../';
import deleteAvatar from '../deleteAvatar';
import updateAvatarId from '../updateAvatarId';

jest.mock('../../../../api');

jest.mock('../', () => ({
    updateAvatar: jest.fn(),
    setAvatarError: jest.fn(),
    updateAvatarStatus: jest.fn()
}));

jest.mock('../../actions/updateAvatarId');
jest.mock('../../helpers/processErrors');

const dispatch = jest.fn();
const getState = jest.fn(() => ({
    changeAvatar: {
        track_id: '123456',
        defaultUrl: '//get-yapic/0/0-0/islands-300'
    },
    common: {
        csrf: '7897cj'
    }
}));

describe('avatars: deleteAvatar', () => {
    afterEach(() => {
        updateAvatar.mockClear();
        updateAvatarStatus.mockClear();
    });

    it('should set loading status before making the request', () => {
        deleteAvatar()(dispatch, getState);
        expect(updateAvatarStatus).toBeCalledWith('loading');
    });

    describe('deleteAvatar: request succeed', () => {
        beforeEach(() => {
            api.__mockSuccess({status: 'ok'});
        });

        afterEach(() => {
            api.request.mockClear();
        });

        it('should call api request with proper params', () => {
            deleteAvatar()(dispatch, getState);
            expect(api.request).toBeCalledWith('avatars/delete', {csrf_token: '7897cj', track_id: '123456'});
        });

        it('should dispatch updateAvatar with proper params', () => {
            deleteAvatar()(dispatch, getState);
            expect(updateAvatar).toBeCalledWith({
                avatarUrl: '//get-yapic/0/0-0/islands-300',
                isDeletePossible: false
            });
            expect(updateAvatarStatus).toBeCalledWith('normal');
        });

        it('should dispatch updateAvatarId', () => {
            deleteAvatar()(dispatch, getState);
            expect(updateAvatarId).toBeCalledWith('//get-yapic/0/0-0/islands-300');
        });
    });

    describe('deleteAvatar: request failed with error', () => {
        beforeEach(() => {
            api.__mockSuccess(['change_avatar.invalid_yapic_response']);
        });

        afterEach(() => {
            api.request.mockClear();
        });

        it('should call api request with proper params', () => {
            deleteAvatar()(dispatch, getState);
            expect(setAvatarError).toBeCalled();
        });
    });
});
