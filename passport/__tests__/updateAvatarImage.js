import updateAvatarImage from '../updateAvatarImage';
import {updateAvatar, updateAvatarStatus} from '../';

jest.mock('../', () => ({
    updateAvatar: jest.fn(),
    updateAvatarStatus: jest.fn()
}));

jest.mock('../updateAvatarId');

const dispatch = jest.fn();
const getState = jest.fn(() => ({
    common: {
        csrf: 'csrf',
        uid: '23452'
    },
    changeAvatar: {
        defaultSize: 'islands-300',
        defaultUrl: 'https://avatars.mdst.yandex.net/get-yapic/0/0-0/islands-300',
        status: 'normal'
    }
}));

describe('avatars: updateAvatarImage', () => {
    it('should dispatch updateAvatar with proper arguments', () => {
        updateAvatarImage('myawesomeurl/')(dispatch, getState);
        expect(updateAvatar).toBeCalledWith({
            avatarUrl: '//myawesomeurl/islands-300',
            backupAvatar: {
                url: '//myawesomeurl/islands-300'
            },
            error: '',
            isDeletePossible: true
        });
        expect(updateAvatarStatus).toBeCalledWith('normal');
    });

    it('should dispatch updateAvatar with default url if url arg is not passed', () => {
        updateAvatarImage()(dispatch, getState);
        expect(updateAvatar).toBeCalledWith({
            avatarUrl: 'https://avatars.mdst.yandex.net/get-yapic/0/0-0/islands-300',
            backupAvatar: {
                url: 'https://avatars.mdst.yandex.net/get-yapic/0/0-0/islands-300'
            },
            error: '',
            isDeletePossible: true
        });
        expect(updateAvatarStatus).toBeCalledWith('normal');
    });
});
