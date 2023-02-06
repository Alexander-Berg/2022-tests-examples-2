import {showAllSettings} from '../../../../social_info/actions';
import {setEditMode} from '../../../../../common/actions';

import * as extracted from '../social_profile.js';

jest.mock('../../../../social_info/actions', () => ({
    showAllSettings: jest.fn()
}));
jest.mock('../../../../../common/actions', () => ({
    setEditMode: jest.fn()
}));

describe('Morda.SocialBlock.SocialProfile', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                dispatch: jest.fn(),
                profile: {
                    profileId: 123
                }
            }
        };
    });
    afterEach(() => {
        setEditMode.mockClear();
    });
    describe('showAllSettingsHandler', () => {
        it('should dispatch setEditMode and showAllSettings', () => {
            extracted.showAllSettingsHandler.call(obj, obj.props.profile.profileId);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(setEditMode).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith('social');
            expect(showAllSettings).toHaveBeenCalledTimes(1);
            expect(showAllSettings).toHaveBeenCalledWith(obj.props.profile.profileId);
        });
    });
});
