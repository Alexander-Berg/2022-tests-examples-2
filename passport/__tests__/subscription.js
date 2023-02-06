import {saveProfileSubscription} from '../../actions/saveProfileSubscription';

import * as extracted from '../subscription.js';

jest.mock('../../actions/saveProfileSubscription', () => ({
    saveProfileSubscription: jest.fn()
}));

const obj = {
    props: {
        dispatch: jest.fn(),
        subscription: {
            profileId: 123,
            sid: 321
        }
    }
};

describe('SocialInfo.Subscription', () => {
    describe('changeSubscription', () => {
        it('should dispatch saveProfileSubscription', () => {
            const {
                dispatch,
                subscription: {profileId, sid}
            } = obj.props;
            const event = {
                target: {
                    checked: false
                }
            };

            extracted.changeSubscription.call(obj, event);
            expect(dispatch).toHaveBeenCalledTimes(1);
            expect(saveProfileSubscription).toHaveBeenCalledTimes(1);
            expect(saveProfileSubscription).toHaveBeenCalledWith(profileId, sid, event.target.checked);
        });
    });
});
