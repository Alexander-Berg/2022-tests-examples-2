import mapDispatchToProps from '../mapDispatchToProps';

import * as redux from 'redux';

import {changeEmail} from '../../../actions/additionalDataRequestActions';
import sendAdditionalDataRequestMetrics from '../../../actions/sendAdditionalDataRequestMetrics';
import sendApiRequest from '../../../actions/sendApiRequest';
import redirectToEmailsPage from '../../../actions/redirectToEmailsPage';

jest.mock('redux', () => ({
    bindActionCreators: jest.fn()
}));
jest.mock('../../../actions/additionalDataRequestActions', () => ({
    changeConfirmationCode: jest.fn()
}));
jest.mock('../../../actions/sendAdditionalDataRequestMetrics');
jest.mock('../../../actions/redirectToEmailsPage');
jest.mock('../../../actions/sendApiRequest');

describe('Components: EmailRequestPage.mapDispatchToProps', () => {
    it('should return action creators', () => {
        const dispatch = jest.fn();

        mapDispatchToProps(dispatch);

        expect(redux.bindActionCreators).toBeCalled();
        expect(redux.bindActionCreators.mock.calls[0][0]).toEqual({
            changeEmail,
            sendApiRequest,
            sendAdditionalDataRequestMetrics,
            redirectToEmailsPage
        });
        expect(redux.bindActionCreators.mock.calls[0][1]).toBe(dispatch);
    });
});
