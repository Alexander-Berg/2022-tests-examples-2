import * as extracted from '../profile.js';

import {showAllSettings, deleteSocialProfile, showDeletePopup} from '../../actions';
import {setEditMode} from '../../../../common/actions';

window.scrollTo = jest.fn();

jest.mock('../../actions', () => ({
    showAllSettings: jest.fn(),
    deleteSocialProfile: jest.fn(),
    showDeletePopup: jest.fn()
}));

jest.mock('../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));

const obj = {
    props: {
        dispatch: jest.fn(),
        profile: {
            profileId: 123
        }
    }
};

describe('SocialInfo.Profile', () => {
    afterEach(() => {
        obj.props.dispatch.mockClear();
        showAllSettings.mockClear();
        showDeletePopup.mockClear();
        deleteSocialProfile.mockClear();
        setEditMode.mockClear();
        window.scrollTo.mockClear();
    });
    describe('scrollToTop', () => {
        it('should call scrollTo', () => {
            obj.props.modal = false;

            extracted.scrollToTop.call(obj);
            expect(window.scrollTo).toHaveBeenCalledTimes(1);
            expect(window.scrollTo).toHaveBeenCalledWith(0, 0);
        });
        it('shouldnt call scrollTo', () => {
            obj.props.modal = true;

            extracted.scrollToTop.call(obj);
            expect(window.scrollTo).toHaveBeenCalledTimes(0);
        });
    });
    describe('hideAllSettings', () => {
        it('should dispatch showAllSettings and showDeletePopup', () => {
            extracted.hideAllSettings.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(showDeletePopup).toHaveBeenCalledTimes(1);
            expect(showDeletePopup).toHaveBeenCalledWith(false);
            expect(showAllSettings).toHaveBeenCalledTimes(1);
            expect(showAllSettings).toHaveBeenCalledWith(null);
        });
    });
    describe('deleteProfile', () => {
        it('should dispatch deleteSocialProfile and showDeletePopup', () => {
            extracted.deleteProfile.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(deleteSocialProfile).toHaveBeenCalledTimes(1);
            expect(deleteSocialProfile).toHaveBeenCalledWith(obj.props.profile.profileId);
            expect(showDeletePopup).toHaveBeenCalledTimes(1);
            expect(showDeletePopup).toHaveBeenCalledWith(false);
        });
    });
    describe('showDeletePopupHandler', () => {
        it('should dispatch showDeletePopup', () => {
            extracted.showDeletePopupHandler.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(showDeletePopup).toHaveBeenCalledTimes(1);
            expect(showDeletePopup).toHaveBeenCalledWith(true);
        });
    });
    describe('hideDeletePopup', () => {
        it('should dispatch showDeletePopup', () => {
            extracted.hideDeletePopup.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(showDeletePopup).toHaveBeenCalledTimes(1);
            expect(showDeletePopup).toHaveBeenCalledWith(false);
        });
    });
});
