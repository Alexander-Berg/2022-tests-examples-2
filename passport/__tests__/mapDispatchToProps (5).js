import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';

import {changeConfirmationCode} from '../../../actions/additionalDataRequestActions';
import sendAdditionalDataRequestMetrics from '../../../actions/sendAdditionalDataRequestMetrics';
import sendApiRequest from '../../../actions/sendApiRequest';
import changeNativeInputValue from '../../../actions/changeNativeInputValue';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../actions/additionalDataRequestActions', () => ({
    changeConfirmationCode: jest.fn()
}));
jest.mock('../../../actions/sendAdditionalDataRequestMetrics');
jest.mock('../../../actions/sendApiRequest');
jest.mock('../../../actions/changeNativeInputValue');

describe('Components: PhoneConfirmationPopup.mapDispatchToProps', () => {
    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            sendAdditionalDataRequestMetrics,
            changeConfirmationCode,
            sendApiRequest,
            changeNativeInputValue
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
