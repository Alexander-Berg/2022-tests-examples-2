import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';

import {changePhoneNumber} from '../../../actions/additionalDataRequestActions';
import sendAdditionalDataRequestMetrics from '../../../actions/sendAdditionalDataRequestMetrics';
import sendApiRequest from '../../../actions/sendApiRequest';
import redirectToPhonesPage from '../../../actions/redirectToPhonesPage';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../actions/additionalDataRequestActions', () => ({
    changeConfirmationCode: jest.fn()
}));
jest.mock('../../../actions/sendAdditionalDataRequestMetrics');
jest.mock('../../../actions/sendApiRequest');
jest.mock('../../../actions/redirectToPhonesPage');

describe('Components: PhoneRequestPage.mapDispatchToProps', () => {
    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            sendApiRequest,
            changePhoneNumber,
            sendAdditionalDataRequestMetrics,
            redirectToPhonesPage
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
