import {allowAuthMethodError} from '../../actions';

import * as extracted from '../profile_items.js';

jest.mock('../../actions', () => ({
    allowAuthMethodError: jest.fn()
}));

const obj = {
    props: {
        dispatch: jest.fn()
    }
};

describe('SocialInfo.ProfileItems', () => {
    describe('allowAuthMethodErrorHandler', () => {
        it('should dispatch allowAuthMethodError', () => {
            extracted.allowAuthMethodErrorHandler.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(allowAuthMethodError).toHaveBeenCalledTimes(1);
        });
    });
});
