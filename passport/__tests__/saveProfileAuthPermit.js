import * as actions from '../actions';
import {saveProfileAuthPermit} from '../actions/saveProfileAuthPermit';
import {saveActionForRepeat, showRegPopup} from '../../../common/actions';
import api from '../../../api';

const data = {
    profileId: 123,
    allowAuth: false,
    sid: 0,
    isEnabled: false,
    error: ''
};
const getStateFactory = (isMobile = true, isTouch = true, isTablet = false) => () => ({
    common: {
        csrf: '',
        uid: 123,
        track_id: 0
    },
    settings: {
        ua: {
            isMobile,
            isTouch,
            isTablet
        }
    }
});

jest.mock('../../../api', () => ({}));
jest.mock('../../../common/actions', () => ({
    saveActionForRepeat: jest.fn(),
    showRegPopup: jest.fn()
}));
jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));

describe('saveProfileAuthPermit', () => {
    beforeEach(() => {
        api.request = jest.fn(() => new $.Deferred().reject());
    });
    afterEach(() => {
        saveActionForRepeat.mockClear();
        showRegPopup.mockClear();
    });

    test('saveProfileAuthPermit calls actions if resolved (no state)', () => {
        const {profileId, allowAuth} = data;
        const spy = jest.spyOn(actions, 'changeProfileAuthPermit');
        const func = saveProfileAuthPermit(profileId, allowAuth);
        const dispatch = jest.fn();

        api.request = jest.fn(() =>
            new $.Deferred().resolve({
                state: ''
            })
        );
        return func(dispatch, getStateFactory())
            .then(() => {
                expect(spy).toHaveBeenCalledTimes(1);
                expect(spy).toHaveBeenCalledWith(profileId, allowAuth);
                expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
                expect(saveActionForRepeat).toHaveBeenCalledWith(saveProfileAuthPermit, profileId, allowAuth);
                spy.mockRestore();
            })
            .promise();
    });
    test('saveProfileAuthPermit calls actions if resolved (with state)', () => {
        const {profileId, allowAuth} = data;
        const spy = jest.spyOn(actions, 'changeProfileAuthPermit');
        const func = saveProfileAuthPermit(profileId, allowAuth);
        const dispatch = jest.fn();

        api.request = jest.fn(() =>
            new $.Deferred().resolve({
                state: 'complete_social_with_login'
            })
        );
        return func(dispatch, getStateFactory())
            .then(() => {
                expect(spy).toHaveBeenCalledTimes(2);
                expect(spy.mock.calls[0]).toEqual([profileId, allowAuth]);
                expect(spy.mock.calls[1]).toEqual([profileId, false]);
                expect(saveActionForRepeat).toHaveBeenCalledWith(saveProfileAuthPermit, profileId, allowAuth);
                expect(showRegPopup).toHaveBeenCalledTimes(1);
                expect(showRegPopup).toHaveBeenCalledWith(true);
                spy.mockRestore();
            })
            .promise();
    });
    test('saveProfileAuthPermit calls actions if rejected', () => {
        const {profileId, allowAuth} = data;
        const spy = jest.spyOn(actions, 'changeProfileAuthPermit');
        const func = saveProfileAuthPermit(profileId, allowAuth);
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().reject());
        return func(dispatch, getStateFactory())
            .catch(() => {
                expect(spy).toHaveBeenCalledTimes(2);
                expect(spy.mock.calls[0]).toEqual([profileId, allowAuth]);
                expect(spy.mock.calls[1]).toEqual([profileId, !allowAuth]);
                expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
                expect(saveActionForRepeat).toHaveBeenCalledWith(saveProfileAuthPermit, profileId, allowAuth);
                spy.mockRestore();
            })
            .promise();
    });
    test('saveProfileAuthPermit calls api.request', () => {
        const func = saveProfileAuthPermit(data.profileId, data.allowAuth);
        const {track_id, csrf: csrf_token, uid} = getStateFactory()().common;

        func(jest.fn(), getStateFactory());
        expect(api.request).toHaveBeenCalledTimes(1);
        expect(api.request).toHaveBeenCalledWith(
            `allowSocialAuth?profile_id=${data.profileId}`,
            {
                track_id,
                csrf_token,
                profile_id: data.profileId,
                set_auth: Number(data.allowAuth),
                uid,
                passErrors: true
            },
            {
                cache: false,
                abortPrevious: true
            }
        );
    });
});
