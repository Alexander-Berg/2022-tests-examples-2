import social from '../reducers';
import {
    GET_SOCIAL_PROFILES_SUCCESS,
    DELETE_SOCIAL_PROFILE_SUCCESS,
    CHANGE_PROFILE_AUTH_PERMIT,
    CHANGE_PROFILE_SUBSCRIPTION,
    SHOW_SOCIAL_PROFILE_ALL_SETTINGS,
    SHOW_DELETE_POPUP,
    SINGLE_AUTH_METHOD_ERROR
} from '../actions';

const state = {
    profiles: [
        {
            profileId: 1,
            allowAuth: true,
            subscriptions: [
                {
                    sid: 123,
                    checked: true
                }
            ]
        },
        {
            profileId: 2,
            allowAuth: true,
            subscriptions: [
                {
                    sid: 123,
                    checked: false
                }
            ]
        }
    ],
    showAddProfiles: true,
    showAllSettings: true,
    isDeletePopupShown: true,
    allowAuthMethodError: {
        profileId: -1,
        error: ''
    }
};

jest.mock('../../../api', () => ({}));

describe('social reducer', () => {
    test(GET_SOCIAL_PROFILES_SUCCESS, () => {
        const profiles = [null, null];

        expect(
            social(state, {
                type: GET_SOCIAL_PROFILES_SUCCESS,
                store: {
                    social: {
                        profiles
                    }
                }
            })
        ).toEqual(
            Object.assign({}, state, {
                profiles,
                showAddProfiles: false
            })
        );
    });

    test(`${DELETE_SOCIAL_PROFILE_SUCCESS} if profile found`, () => {
        expect(
            social(state, {
                type: DELETE_SOCIAL_PROFILE_SUCCESS,
                profileId: state.profiles[0].profileId
            })
        ).toEqual(
            Object.assign({}, state, {
                profiles: state.profiles.slice(1),
                showAllSettings: !state.showAllSettings
            })
        );
    });
    test(`${DELETE_SOCIAL_PROFILE_SUCCESS} if profile not found`, () => {
        expect(
            social(state, {
                type: DELETE_SOCIAL_PROFILE_SUCCESS,
                profileId: -1
            })
        ).toEqual(
            Object.assign({}, state, {
                profiles: state.profiles,
                showAllSettings: state.showAllSettings
            })
        );
    });

    test(`${CHANGE_PROFILE_AUTH_PERMIT} if profile found`, () => {
        const newProfile = Object.assign({}, state.profiles[0], {
            allowAuth: !state.profiles[0].allowAuth
        });

        expect(
            social(state, {
                type: CHANGE_PROFILE_AUTH_PERMIT,
                profileId: state.profiles[0].profileId,
                allowAuth: !state.profiles[0].allowAuth
            })
        ).toEqual(
            Object.assign({}, state, {
                profiles: [newProfile, ...state.profiles.slice(1)]
            })
        );
    });
    test(`${CHANGE_PROFILE_AUTH_PERMIT} if profile not found`, () => {
        expect(
            social(state, {
                type: CHANGE_PROFILE_AUTH_PERMIT,
                profileId: -1,
                allowAuth: false
            })
        ).toEqual(
            Object.assign({}, state, {
                profiles: state.profiles
            })
        );
    });

    test(`${CHANGE_PROFILE_SUBSCRIPTION} if profile found`, () => {
        const newProfile = Object.assign({}, state.profiles[0], {
            subscriptions: [
                Object.assign({}, state.profiles[0].subscriptions[0], {
                    checked: !state.profiles[0].subscriptions[0].checked
                }),
                ...state.profiles[0].subscriptions.slice(1)
            ]
        });

        expect(
            social(state, {
                type: CHANGE_PROFILE_SUBSCRIPTION,
                profileId: state.profiles[0].profileId,
                sid: state.profiles[0].subscriptions[0].sid,
                isEnabled: !state.profiles[0].subscriptions[0].checked
            })
        ).toEqual(
            Object.assign({}, state, {
                profiles: [newProfile, ...state.profiles.slice(1)]
            })
        );
    });
    test(`${CHANGE_PROFILE_SUBSCRIPTION} if profile not found`, () => {
        expect(
            social(state, {
                type: CHANGE_PROFILE_SUBSCRIPTION,
                profileId: -1,
                sid: -1,
                isEnabled: false
            })
        ).toEqual(
            Object.assign({}, state, {
                profiles: state.profiles
            })
        );
    });

    test(SHOW_SOCIAL_PROFILE_ALL_SETTINGS, () => {
        expect(
            social(state, {
                type: SHOW_SOCIAL_PROFILE_ALL_SETTINGS,
                profileId: 123
            })
        ).toEqual(
            Object.assign({}, state, {
                showAllSettings: 123
            })
        );
    });
    test(SHOW_DELETE_POPUP, () => {
        expect(
            social(state, {
                type: SHOW_DELETE_POPUP,
                shown: true
            })
        ).toEqual(
            Object.assign({}, state, {
                isDeletePopupShown: true
            })
        );
    });
    test(SINGLE_AUTH_METHOD_ERROR, () => {
        const error = 'unknown vzhukh happened';

        expect(
            social(state, {
                type: SINGLE_AUTH_METHOD_ERROR,
                profileId: 123,
                error
            })
        ).toEqual(
            Object.assign({}, state, {
                allowAuthMethodError: {
                    profileId: 123,
                    error
                }
            })
        );
    });
    test('action not found', () => {
        expect(social(state, {type: 'LOL_ACTION_NOT_FOUND'})).toEqual(state);
    });
    test('state default value', () => {
        expect(social(undefined, {type: 'LOL_ACTION_NOT_FOUND'})).toEqual({});
    });
});
