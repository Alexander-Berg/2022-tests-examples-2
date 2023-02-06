import sendApiRequest from '../../actions/send_api_request';
import requestPhoneConfirmationCode from '../../actions/request_phone_confirmation_code';
import submitPhoneConfirmationCode from '../../actions/submit_phone_confirmation_code';
import approveActualPhone from '../../actions/approve_actual_phone';
import redirectToPhonesPage from '../../actions/redirect_to_phones_page';
import skipAdditionalData from '../../actions/skip_additional_data';
import {changePhoneNumber, changeConfirmationCode, changeConfirmationCodeSentStatus, clearErrors} from '../../actions';
import {
    goBack,
    handlePhoneChange,
    handleConfirmationCodeChange,
    approvePhone,
    sentConfirmationCode,
    confirmActualPhone,
    goToPhonesPage,
    goEnterPhone
} from '../request_phone.js';

jest.mock('../../actions/send_api_request');
jest.mock('../../actions/request_phone_confirmation_code');
jest.mock('../../actions/submit_phone_confirmation_code');
jest.mock('../../actions/approve_actual_phone');
jest.mock('../../actions/redirect_to_phones_page');
jest.mock('../../actions/skip_additional_data');
jest.mock('../../actions', () => ({
    changePhoneNumber: jest.fn(),
    changeConfirmationCode: jest.fn(),
    changeConfirmationCodeSentStatus: jest.fn(),
    clearErrors: jest.fn()
}));

const props = {
    dispatch: jest.fn(),
    phoneNumber: '+71234567890',
    phoneId: '1234',
    confirmationCode: 'code'
};

const preventDefault = jest.fn();

describe('Component: RequestPhone', () => {
    beforeEach(() => {
        sendApiRequest.mockImplementation(() => () => {});
        requestPhoneConfirmationCode.mockImplementation(() => () => {});
        submitPhoneConfirmationCode.mockImplementation(() => () => {});
        approveActualPhone.mockImplementation(() => () => {});
        redirectToPhonesPage.mockImplementation(() => () => {});
        skipAdditionalData.mockImplementation(() => () => {});
    });

    afterEach(() => {
        props.dispatch.mockClear();
        sendApiRequest.mockClear();
        requestPhoneConfirmationCode.mockClear();
        submitPhoneConfirmationCode.mockClear();
        approveActualPhone.mockClear();
        redirectToPhonesPage.mockClear();
        skipAdditionalData.mockClear();
        preventDefault.mockClear();
        clearErrors.mockClear();
        changeConfirmationCode.mockClear();
    });

    it('should dispatch sendApiRequest action with skipAdditionalData action in args', () => {
        goBack.call({props});

        expect(props.dispatch).toBeCalled();
        expect(sendApiRequest).toBeCalledWith(skipAdditionalData);
    });

    it('should dispatch changePhoneNumber action with number in args', () => {
        handlePhoneChange.call({props}, {target: {value: props.phoneNumber}});

        expect(props.dispatch).toBeCalled();
        expect(changePhoneNumber).toBeCalledWith(props.phoneNumber);
    });

    it('should dispatch changeConfirmationCode action with code in args', () => {
        handleConfirmationCodeChange.call({props}, {target: {value: props.confirmationCode}});

        expect(props.dispatch).toBeCalled();
        expect(changeConfirmationCode).toBeCalledWith(props.confirmationCode);
    });

    it(
        'should dispatch sendApiRequest action with submitPhoneConfirmationCode ' +
            'action and confirmationCode in args',
        () => {
            approvePhone.call({props}, {preventDefault});

            expect(props.dispatch).toBeCalled();
            expect(preventDefault).toBeCalled();
            expect(sendApiRequest).toBeCalledWith(submitPhoneConfirmationCode, props.confirmationCode);
        }
    );

    it('should dispatch sendApiRequest action with requestPhoneConfirmationCode action and phoneNumber in args', () => {
        sentConfirmationCode.call({props}, {preventDefault});

        expect(props.dispatch).toBeCalled();
        expect(preventDefault).toBeCalled();
        expect(sendApiRequest).toBeCalledWith(requestPhoneConfirmationCode, props.phoneNumber);
    });

    it('should dispatch sendApiRequest action with approveActualPhone action and phoneId in args', () => {
        confirmActualPhone.call({props}, {preventDefault});

        expect(props.dispatch).toBeCalled();
        expect(preventDefault).toBeCalled();
        expect(sendApiRequest).toBeCalledWith(approveActualPhone, props.phoneId);
    });

    it('should dispatch redirectToPhonesPage action', () => {
        goToPhonesPage.call({props});

        expect(props.dispatch).toBeCalled();
        expect(redirectToPhonesPage).toBeCalled();
    });

    it('should dispatch changeConfirmationCodeSentStatus action', () => {
        goEnterPhone.call({props});

        expect(props.dispatch).toBeCalled();
        expect(props.dispatch.mock.calls.length).toBe(3);
        expect(clearErrors).toBeCalled();
        expect(changeConfirmationCodeSentStatus).toBeCalled();
        expect(changeConfirmationCodeSentStatus).toBeCalledWith(false);
        expect(changeConfirmationCode).toBeCalled();
        expect(changeConfirmationCode).toBeCalledWith('');
    });
});
