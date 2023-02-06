import * as actions from '../actions';
import {saveProfileSubscription} from '../actions/saveProfileSubscription';
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

describe('saveProfileSubscription', () => {
    test('saveProfileSubscription calls actions if resolved', () => {
        const {profileId, sid, isEnabled} = data;
        const func = saveProfileSubscription(profileId, sid, isEnabled);
        const dispatch = jest.fn();
        const spy = jest.spyOn(actions, 'changeSubscription');

        api.request = jest.fn(() => new $.Deferred().resolve());
        return func(dispatch, getStateFactory())
            .then(() => {
                expect(spy).toHaveBeenCalledTimes(1);
                expect(spy).toHaveBeenCalledWith(profileId, sid, isEnabled);
                spy.mockRestore();
            })
            .promise();
    });
    test('saveProfileSubscription calls actions if rejected', () => {
        const {profileId, sid, isEnabled} = data;
        const func = saveProfileSubscription(profileId, sid, isEnabled);
        const dispatch = jest.fn();
        const spy = jest.spyOn(actions, 'changeSubscription');

        return func(dispatch, getStateFactory())
            .catch(() => {
                expect(spy).toHaveBeenCalledTimes(2);
                expect(spy.mock.calls[0]).toEqual([profileId, sid, isEnabled]);
                expect(spy.mock.calls[1]).toEqual([profileId, sid, !isEnabled]);
                spy.mockRestore();
            })
            .promise();
    });
    test('saveProfileSubscription calls api.request if isEnabled is true', () => {
        const {profileId, sid} = data;
        const isEnabled = true;
        const func = saveProfileSubscription(profileId, sid, isEnabled);
        const {track_id, csrf: csrf_token, uid} = getStateFactory()().common;

        api.request = jest.fn(() => new $.Deferred().resolve());
        func(jest.fn(), getStateFactory());
        expect(api.request).toHaveBeenCalledTimes(1);
        expect(api.request).toHaveBeenCalledWith(
            'enableSocialSubscribe',
            {
                csrf_token,
                track_id,
                profile_id: profileId,
                uid,
                sid
            },
            {
                cache: false,
                abortPrevious: true
            }
        );
    });
    test('saveProfileSubscription calls api.request if isEnabled is false', () => {
        const {profileId, sid} = data;
        const isEnabled = true;
        const func = saveProfileSubscription(profileId, sid, isEnabled);
        const {track_id, csrf: csrf_token, uid} = getStateFactory()().common;

        api.request = jest.fn(() => new $.Deferred().resolve());
        func(jest.fn(), getStateFactory());
        expect(api.request).toHaveBeenCalledTimes(1);
        expect(api.request).toHaveBeenCalledWith(
            'enableSocialSubscribe',
            {
                csrf_token,
                track_id,
                profile_id: profileId,
                uid,
                sid
            },
            {
                cache: false,
                abortPrevious: true
            }
        );
    });
});
