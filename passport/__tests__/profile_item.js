import {push} from 'connected-react-router';

import * as extracted from '../profile_item.js';

import {showAllSettings, showRegPopup} from '../../actions';
import {saveProfileAuthPermit} from '../../actions/saveProfileAuthPermit';

jest.mock('../../actions', () => ({
    showAllSettings: jest.fn(),
    showRegPopup: jest.fn()
}));
jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../../actions/saveProfileAuthPermit');

describe('SocialInfo.ProfileItem', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                dispatch: jest.fn(),
                profile: {
                    profileId: 123,
                    allowAuth: false
                },
                isSocialchik: false,
                modal: false
            }
        };
    });
    afterEach(() => {
        showAllSettings.mockClear();
        saveProfileAuthPermit.mockClear();
        showRegPopup.mockClear();
        push.mockClear();
    });
    describe('showAllSettingsHandler', () => {
        it('should call push', () => {
            extracted.showAllSettingsHandler.call(obj);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith(`/profile/social/${obj.props.profile.profileId}`);
        });
        it('should dispatch showAllSettings', () => {
            const {
                dispatch,
                profile: {profileId}
            } = obj.props;

            obj.props.modal = true;

            extracted.showAllSettingsHandler.call(obj);
            expect(dispatch).toHaveBeenCalledTimes(1);
            expect(showAllSettings).toHaveBeenCalledTimes(1);
            expect(showAllSettings).toHaveBeenCalledWith(profileId);
        });
    });
    describe(',saveProfileAuthPermitHandler', () => {
        it('should dispatch saveProfileAuthPermit', () => {
            const {
                profile: {profileId, allowAuth},
                dispatch
            } = obj.props;

            extracted.saveProfileAuthPermitHandler.call(obj);
            expect(dispatch).toHaveBeenCalledTimes(1);
            expect(saveProfileAuthPermit).toHaveBeenCalledTimes(1);
            expect(saveProfileAuthPermit).toHaveBeenCalledWith(profileId, !allowAuth);
        });
    });
});
