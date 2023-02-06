import sendApiRequest from '../../actions/send_api_request';
import requestEmailConfirmationCode from '../../actions/request_email_confirmation_code';
import submitEmailConfirmationCode from '../../actions/submit_email_confirmation_code';
import redirectToEmailsPage from '../../actions/redirect_to_emails_page';
import skipAdditionalData from '../../actions/skip_additional_data';
import setupConfirmedEmail from '../../actions/setup_confirmed_email';
import {changeEmail, changeConfirmationCode, changeConfirmationCodeSentStatus, clearErrors} from '../../actions';
import {
    goBack,
    handleEmailChange,
    handleConfirmationCodeChange,
    approveEmail,
    sentConfirmationCode,
    confirmRestoreEmail,
    goToEmailsPage,
    goEnterEmail
} from '../request_email.js';

jest.mock('../../actions/send_api_request');
jest.mock('../../actions/request_email_confirmation_code');
jest.mock('../../actions/submit_email_confirmation_code');
jest.mock('../../actions/redirect_to_emails_page');
jest.mock('../../actions/skip_additional_data');
jest.mock('../../actions/setup_confirmed_email');
jest.mock('../../actions', () => ({
    changeEmail: jest.fn(),
    changeConfirmationCode: jest.fn(),
    changeConfirmationCodeSentStatus: jest.fn(),
    clearErrors: jest.fn()
}));

const props = {
    dispatch: jest.fn(),
    confirmationCode: 'code',
    email: 'example@email.ru'
};

const preventDefault = jest.fn();

describe('Component: RequestEmail', () => {
    beforeEach(() => {
        sendApiRequest.mockImplementation(() => () => {});
        requestEmailConfirmationCode.mockImplementation(() => () => {});
        submitEmailConfirmationCode.mockImplementation(() => () => {});
        redirectToEmailsPage.mockImplementation(() => () => {});
        skipAdditionalData.mockImplementation(() => () => {});
        setupConfirmedEmail.mockImplementation(() => () => {});
    });

    afterEach(() => {
        props.dispatch.mockClear();
        sendApiRequest.mockClear();
        requestEmailConfirmationCode.mockClear();
        submitEmailConfirmationCode.mockClear();
        redirectToEmailsPage.mockClear();
        skipAdditionalData.mockClear();
        setupConfirmedEmail.mockClear();
        preventDefault.mockClear();
        clearErrors.mockClear();
        changeConfirmationCode.mockClear();
    });

    it('should dispatch sendApiRequest action with skipAdditionalData action in args', () => {
        goBack.call({props});

        expect(props.dispatch).toBeCalled();
        expect(sendApiRequest).toBeCalledWith(skipAdditionalData);
    });

    it('should dispatch changeEmail with value', () => {
        handleEmailChange.call({props}, {target: {value: props.email}});

        expect(props.dispatch).toBeCalled();
        expect(changeEmail).toBeCalledWith(props.email);
    });

    it('should dispatch changeConfirmationCode with value', () => {
        handleConfirmationCodeChange.call({props}, {target: {value: props.confirmationCode}});

        expect(props.dispatch).toBeCalled();
        expect(changeConfirmationCode).toBeCalledWith(props.confirmationCode);
    });

    it(
        'should dispatch sendApiRequest action with submitEmailConfirmationCode ' +
            'action and confirmationCode in args',
        () => {
            approveEmail.call({props}, {preventDefault});

            expect(props.dispatch).toBeCalled();
            expect(preventDefault).toBeCalled();
            expect(sendApiRequest).toBeCalledWith(submitEmailConfirmationCode, props.confirmationCode);
        }
    );

    it('should dispatch sendApiRequest action with requestEmailConfirmationCode action and email in args', () => {
        sentConfirmationCode.call({props}, {preventDefault});

        expect(props.dispatch).toBeCalled();
        expect(preventDefault).toBeCalled();
        expect(sendApiRequest).toBeCalledWith(requestEmailConfirmationCode, props.email);
    });

    it('should dispatch sendApiRequest action with setupConfirmedEmail action and email in args', () => {
        confirmRestoreEmail.call({props}, {preventDefault});

        expect(props.dispatch).toBeCalled();
        expect(preventDefault).toBeCalled();
        expect(sendApiRequest).toBeCalledWith(setupConfirmedEmail, props.email);
    });

    it('should dispatch redirectToEmailsPage action', () => {
        goToEmailsPage.call({props});

        expect(props.dispatch).toBeCalled();
        expect(redirectToEmailsPage).toBeCalled();
    });

    it('should dispatch changeConfirmationCodeSentStatus action', () => {
        goEnterEmail.call({props});

        expect(props.dispatch).toBeCalled();
        expect(props.dispatch.mock.calls.length).toBe(3);
        expect(clearErrors).toBeCalled();
        expect(changeConfirmationCodeSentStatus).toBeCalled();
        expect(changeConfirmationCodeSentStatus).toBeCalledWith(false);
        expect(changeConfirmationCode).toBeCalled();
        expect(changeConfirmationCode).toBeCalledWith('');
    });
});
