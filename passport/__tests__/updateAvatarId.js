import updateAvatarId from '../updateAvatarId';
import {updateHeaderAvatar} from '@blocks/morda/components/header/actions';
import {updateMainAvatar} from '@blocks/morda/personal_info/actions';
import {updateAvatar} from '../';

jest.mock('@blocks/morda/components/header/actions', () => ({
    updateHeaderAvatar: jest.fn()
}));

jest.mock('@blocks/morda/personal_info/actions', () => ({
    updateMainAvatar: jest.fn()
}));

jest.mock('../', () => ({
    updateAvatar: jest.fn()
}));

const dispatch = jest.fn();
const getState = jest.fn(() => ({
    person: {avatarId: '0-0'},
    settings: {
        ua: {
            isMobile: false
        }
    },
    changeAvatar: {
        isByUrl: false,
        queryUid: '',
        backupAvatar: {
            url: '//avatars.mdst.yandex.net/get-yapic/1234/SomESymbols/islands-300'
        }
    }
}));
const url = '//avatars.mdst.yandex.net/get-yapic/1234/SomESymbols/islands-300';

describe('avatars: updateAvatarId', () => {
    it('should dispatch updateMainAvatar with proper arguments', () => {
        updateAvatarId(url)(dispatch, getState);
        expect(updateMainAvatar).toBeCalledWith('1234/SomESymbols');
    });

    it('should dispatch updateHeaderAvatar if queryUid is provided in the state', () => {
        updateAvatarId(url)(dispatch, getState);
        expect(updateHeaderAvatar).toBeCalledWith('1234/SomESymbols');
    });

    it('should dispatch updateAvatar with proper arguments if queryUid and isPhone properties are provided', () => {
        const getState = jest.fn(() => ({
            person: {avatarId: '0-0'},
            settings: {
                ua: {
                    isMobile: true
                }
            },
            changeAvatar: {
                isByUrl: false,
                queryUid: '5235325',
                backupAvatar: {
                    url: '//avatars.mdst.yandex.net/get-yapic/1234/SomESymbols/islands-300'
                }
            }
        }));

        updateAvatarId(url)(dispatch, getState);
        expect(updateAvatar).toBeCalledWith({queryUid: ''});
    });
});
