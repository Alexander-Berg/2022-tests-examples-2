import * as actions from '../actions';
import {saveActionForRepeat, showRegPopup} from '../../../common/actions';
import {saveProfileAuthPermit} from '../actions/saveProfileAuthPermit';
import {saveProfileSubscription} from '../actions/saveProfileSubscription';
import api from '../../../api';
import {push} from 'connected-react-router';

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

describe('actions', () => {
    beforeEach(() => {
        api.request = jest.fn(() => new $.Deferred().reject());
    });
    afterEach(() => {
        saveActionForRepeat.mockClear();
        showRegPopup.mockClear();
        push.mockClear();
    });
    test('changeProfileAuthPermit', () => {
        const {profileId, allowAuth} = data;

        expect(actions.changeProfileAuthPermit(profileId, allowAuth)).toEqual({
            type: actions.CHANGE_PROFILE_AUTH_PERMIT,
            profileId,
            allowAuth
        });
    });

    test('saveProfileAuthPermit returns function', () => {
        expect(typeof saveProfileAuthPermit()).toEqual('function');
    });
    test('saveProfileAuthPermit calls dispatch if resolved (no state)', () => {
        const func = saveProfileAuthPermit(data.profileId, data.allowAuth);
        const dispatch = jest.fn();

        api.request = jest.fn(() =>
            new $.Deferred().resolve({
                state: ''
            })
        );
        return func(dispatch, getStateFactory())
            .then(() => {
                expect(dispatch).toHaveBeenCalledTimes(2);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.CHANGE_PROFILE_AUTH_PERMIT,
                    profileId: data.profileId,
                    allowAuth: data.allowAuth
                });
            })
            .promise();
    });
    test('saveProfileAuthPermit calls dispatch if resolved (with state)', () => {
        const func = saveProfileAuthPermit(data.profileId, data.allowAuth);
        const dispatch = jest.fn();

        api.request = jest.fn(() =>
            new $.Deferred().resolve({
                state: 'complete_social_with_login'
            })
        );
        return func(dispatch, getStateFactory())
            .then(() => {
                expect(dispatch).toHaveBeenCalledTimes(4);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.CHANGE_PROFILE_AUTH_PERMIT,
                    profileId: data.profileId,
                    allowAuth: data.allowAuth
                });
                expect(dispatch.mock.calls[2][0]).toEqual({
                    type: actions.CHANGE_PROFILE_AUTH_PERMIT,
                    profileId: data.profileId,
                    allowAuth: false
                });
            })
            .promise();
    });
    test('saveProfileAuthPermit calls dispatch if rejected', () => {
        const func = saveProfileAuthPermit(data.profileId, data.allowAuth);
        const dispatch = jest.fn();

        return func(dispatch, getStateFactory())
            .catch(() => {
                expect(dispatch).toHaveBeenCalledTimes(3);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.CHANGE_PROFILE_AUTH_PERMIT,
                    profileId: data.profileId,
                    allowAuth: data.allowAuth
                });
                expect(dispatch.mock.calls[2][0]).toEqual({
                    type: actions.CHANGE_PROFILE_AUTH_PERMIT,
                    profileId: data.profileId,
                    allowAuth: !data.allowAuth
                });
            })
            .promise();
    });
    test('getSocialProfiles returns function', () => {
        expect(typeof actions.getSocialProfiles()).toEqual('function');
    });
    test('getSocialProfiles calls dispatch if resolved', () => {
        const func = actions.getSocialProfiles();
        const store = 'store';
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().resolve(store));
        return func(dispatch)
            .then(() => {
                expect(dispatch).toHaveBeenCalledTimes(2);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.GET_SOCIAL_PROFILES
                });
                expect(dispatch.mock.calls[1][0]).toEqual({
                    type: actions.GET_SOCIAL_PROFILES_SUCCESS,
                    store
                });
            })
            .promise();
    });
    test('getSocialProfiles calls dispatch if rejected', () => {
        const func = actions.getSocialProfiles();
        const error = 'error';
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().reject(error));
        return func(dispatch)
            .catch(() => {
                expect(dispatch).toHaveBeenCalledTimes(2);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.GET_SOCIAL_PROFILES
                });
                expect(dispatch.mock.calls[1][0]).toEqual({
                    type: actions.GET_SOCIAL_PROFILES_ERROR,
                    error
                });
            })
            .promise();
    });
    test('getSocialProfiles calls api.request', () => {
        const func = actions.getSocialProfiles();

        func(jest.fn());
        expect(api.request).toHaveBeenCalledTimes(1);
        expect(api.request).toHaveBeenCalledWith('get.profile', {});
    });

    test('deleteSocialProfile returns function', () => {
        expect(typeof actions.deleteSocialProfile()).toEqual('function');
    });
    test('deleteSocialProfile calls push', () =>
        new Promise((res, rej) => {
            const func = actions.deleteSocialProfile(data.profileId);

            api.request = jest.fn(() => new $.Deferred().resolve());
            func(jest.fn(), getStateFactory()).then(() => {
                try {
                    expect(push).toHaveBeenCalledTimes(1);
                    expect(push).toHaveBeenCalledWith('/profile/social');
                } catch (e) {
                    rej(e);
                    return;
                }
                push.mockClear();
                func(jest.fn(), getStateFactory(false)).then(() => {
                    try {
                        expect(push).toHaveBeenCalledTimes(1);
                        expect(push).toHaveBeenCalledWith('/profile/social');
                    } catch (e) {
                        rej(e);
                        return;
                    }
                    push.mockClear();
                    func(jest.fn(), getStateFactory(false, false, true)).then(() => {
                        try {
                            expect(push).toHaveBeenCalledTimes(0);
                            res();
                        } catch (e) {
                            rej(e);
                        }
                    });
                });
            });
        }));
    test('deleteSocialProfile calls dispatch if resolved', () => {
        const func = actions.deleteSocialProfile(data.profileId);
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().resolve());
        return func(dispatch, getStateFactory())
            .then(() => {
                expect(dispatch).toHaveBeenCalledTimes(4);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.DELETE_SOCIAL_PROFILE,
                    profileId: data.profileId
                });
                expect(dispatch.mock.calls[3][0]).toEqual({
                    type: actions.DELETE_SOCIAL_PROFILE_SUCCESS,
                    profileId: data.profileId
                });
            })
            .promise();
    });
    test('deleteSocialProfile calls dispatch if rejected (no error)', () => {
        const func = actions.deleteSocialProfile(data.profileId);
        const response = {};
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().reject(response));
        return func(dispatch, getStateFactory())
            .catch(() => {
                expect(dispatch).toHaveBeenCalledTimes(3);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.DELETE_SOCIAL_PROFILE,
                    profileId: data.profileId
                });
                expect(dispatch.mock.calls[2][0]).toEqual({
                    type: actions.DELETE_SOCIAL_PROFILE_ERROR,
                    error: response
                });
            })
            .promise();
    });
    test('deleteSocialProfile calls dispatch if rejected (with error)', () => {
        const func = actions.deleteSocialProfile(data.profileId);
        const response = {
            errors: ['social_profile.single_auth_method']
        };
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().reject(response));
        return func(dispatch, getStateFactory())
            .catch(() => {
                expect(dispatch).toHaveBeenCalledTimes(4);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.DELETE_SOCIAL_PROFILE,
                    profileId: data.profileId
                });
                expect(dispatch.mock.calls[3][0]).toEqual({
                    type: actions.DELETE_SOCIAL_PROFILE_ERROR,
                    error: response
                });
            })
            .promise();
    });

    test('deleteSocialProfile calls actions if resolved', () => {
        const func = actions.deleteSocialProfile(data.profileId);
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().resolve());
        return func(dispatch, getStateFactory())
            .then(() => {
                expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
                expect(saveActionForRepeat).toHaveBeenCalledWith(actions.deleteSocialProfile, data.profileId);
            })
            .promise();
    });
    test('deleteSocialProfile calls actions if rejected (no error)', () => {
        const func = actions.deleteSocialProfile(data.profileId);
        const response = {};
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().reject(response));
        return func(dispatch, getStateFactory())
            .catch(() => {
                expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
                expect(saveActionForRepeat).toHaveBeenCalledWith(actions.deleteSocialProfile, data.profileId);
            })
            .promise();
    });
    test('deleteSocialProfile calls actions if rejected (with error)', () => {
        const func = actions.deleteSocialProfile(data.profileId);
        const response = {
            errors: ['social_profile.single_auth_method']
        };
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().reject(response));
        return func(dispatch, getStateFactory())
            .catch(() => {
                expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
                expect(saveActionForRepeat).toHaveBeenCalledWith(actions.deleteSocialProfile, data.profileId);
                expect(showRegPopup).toHaveBeenCalledTimes(1);
                expect(showRegPopup).toHaveBeenCalledWith(true);
            })
            .promise();
    });
    test('deleteSocialProfile calls api.request', () => {
        const func = actions.deleteSocialProfile(data.profileId, data.allowAuth);
        const {track_id, csrf: csrf_token, uid} = getStateFactory()().common;

        api.request = jest.fn(() => new $.Deferred().resolve());
        func(jest.fn(), getStateFactory());
        expect(api.request).toHaveBeenCalledTimes(1);
        expect(api.request).toHaveBeenCalledWith('delSocialProfile', {
            track_id,
            csrf_token,
            profile_id: data.profileId,
            uid,
            passErrors: true
        });
    });

    test('saveProfileSubscription returns function', () => {
        expect(typeof saveProfileSubscription()).toEqual('function');
    });
    test('saveProfileSubscription calls dispatch if resolved', () => {
        const {profileId, sid, isEnabled} = data;
        const func = saveProfileSubscription(profileId, sid, isEnabled);
        const dispatch = jest.fn();

        api.request = jest.fn(() => new $.Deferred().resolve());
        return func(dispatch, getStateFactory())
            .then(() => {
                expect(dispatch).toHaveBeenCalledTimes(1);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.CHANGE_PROFILE_SUBSCRIPTION,
                    profileId,
                    sid,
                    isEnabled
                });
            })
            .promise();
    });
    test('saveProfileSubscription calls dispatch if rejected', () => {
        const {profileId, sid, isEnabled} = data;
        const func = saveProfileSubscription(profileId, sid, isEnabled);
        const dispatch = jest.fn();

        return func(dispatch, getStateFactory())
            .catch(() => {
                expect(dispatch).toHaveBeenCalledTimes(2);
                expect(dispatch.mock.calls[0][0]).toEqual({
                    type: actions.CHANGE_PROFILE_SUBSCRIPTION,
                    profileId,
                    sid,
                    isEnabled
                });
                expect(dispatch.mock.calls[1][0]).toEqual({
                    type: actions.CHANGE_PROFILE_SUBSCRIPTION,
                    profileId,
                    sid,
                    isEnabled: !isEnabled
                });
            })
            .promise();
    });

    test('showAllSettings', () => {
        expect(actions.showAllSettings(data.profileId)).toEqual({
            type: actions.SHOW_SOCIAL_PROFILE_ALL_SETTINGS,
            profileId: data.profileId
        });
    });
    test('showDeletePopup', () => {
        expect(actions.showDeletePopup(true)).toEqual({
            type: actions.SHOW_DELETE_POPUP,
            shown: true
        });
    });
    test('changeSubscription', () => {
        const {profileId, sid, isEnabled} = data;

        expect(actions.changeSubscription(profileId, sid, isEnabled)).toEqual({
            type: actions.CHANGE_PROFILE_SUBSCRIPTION,
            profileId,
            sid,
            isEnabled
        });
    });
    test('allowAuthMethodError with arguments', () => {
        expect(actions.allowAuthMethodError(data.profileId, data.error)).toEqual({
            type: actions.SINGLE_AUTH_METHOD_ERROR,
            profileId: data.profileId,
            error: data.error
        });
    });
    test('allowAuthMethodError no arguments', () => {
        expect(actions.allowAuthMethodError()).toEqual({
            type: actions.SINGLE_AUTH_METHOD_ERROR,
            profileId: 0,
            error: ''
        });
    });
});
