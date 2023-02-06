import initDeleteProcess from '../init_delete_process';
import checkCaptcha from '../../thunks/check_captcha';
import sendConfirmation from '../../thunks/send_confirmation';
import checkCode from '../../thunks/check_code';
import questionCheck from '../../thunks/question_check';
import processError from '../process_error';
import {setModalStatus} from '../../actions';

jest.mock('../../actions', () => ({
    setModalStatus: jest.fn()
}));

jest.mock('../../thunks/check_captcha');
jest.mock('../process_error');
jest.mock('../../thunks/send_confirmation');
jest.mock('../../thunks/check_code');
jest.mock('../../thunks/question_check');

const dispatch = jest.fn();

describe('initDeleteProcess', () => {
    beforeEach(() => {
        checkCaptcha.mockImplementation(() => jest.fn());
        processError.mockImplementation(() => jest.fn());
        sendConfirmation.mockImplementation(() => jest.fn());
        checkCode.mockImplementation(() => jest.fn());
        questionCheck.mockImplementation(() => jest.fn());
    });

    afterEach(() => {
        checkCaptcha.mockClear();
        processError.mockClear();
        sendConfirmation.mockClear();
        checkCode.mockClear();
        questionCheck.mockClear();
    });

    it('should dispatch setModalStatus if confirmation should be skipped', () => {
        const getState = () => ({
            deleteAccount: {
                isFetching: false,
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: false,
                confirmation: {
                    method: 'skip',
                    status: 'unconfirmed'
                },
                form: {
                    code: '',
                    answer: '',
                    captcha: ''
                }
            }
        });

        initDeleteProcess()(dispatch, getState);
        expect(setModalStatus).toBeCalled();
    });

    it('should dispatch checkCaptcha if confirmation method is captcha', () => {
        const getState = () => ({
            deleteAccount: {
                isFetching: false,
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: false,
                confirmation: {
                    method: 'captcha',
                    status: 'unconfirmed'
                },
                form: {
                    code: '',
                    answer: '',
                    captcha: ''
                }
            }
        });

        initDeleteProcess()(dispatch, getState);
        expect(checkCaptcha).toBeCalled();
    });

    it('should dispatch processError with captcha error if captcha not filled', () => {
        const getState = () => ({
            deleteAccount: {
                isFetching: false,
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: false,
                confirmation: {
                    method: 'phone',
                    status: 'unconfirmed'
                },
                form: {
                    code: '',
                    answer: '',
                    captcha: ''
                }
            }
        });

        initDeleteProcess()(dispatch, getState);
        expect(processError).toBeCalled();
        expect(processError).toBeCalledWith('captcha', 'captcha.empty');
    });

    it('should dispatch sendConfirmation if code not filled', () => {
        const getState = () => ({
            deleteAccount: {
                isFetching: false,
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: false,
                confirmation: {
                    method: 'phone',
                    status: 'unconfirmed'
                },
                form: {
                    code: '',
                    answer: '',
                    captcha: 'testcaptcha'
                }
            }
        });
        const formData = {
            code: '',
            answer: '',
            captcha: 'testcaptcha'
        };

        initDeleteProcess()(dispatch, getState);
        expect(sendConfirmation).toBeCalled();
        expect(sendConfirmation).toBeCalledWith(formData, 'phone');
    });

    it('should dispatch checkCode if code is filled', () => {
        const getState = () => ({
            deleteAccount: {
                isFetching: false,
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: false,
                confirmation: {
                    method: 'phone',
                    status: 'unconfirmed'
                },
                form: {
                    code: '123',
                    answer: '',
                    captcha: 'testcaptcha'
                }
            }
        });

        initDeleteProcess()(dispatch, getState);
        expect(checkCode).toBeCalled();
        expect(checkCode).toBeCalledWith('123', 'phone');
    });

    it('should dispatch questionCheck if confirmation method neither phone nor email', () => {
        const getState = () => ({
            deleteAccount: {
                isFetching: false,
                isModalOpened: false,
                isSocialchik: false,
                isPddAdmin: false,
                confirmation: {
                    method: 'question',
                    status: 'unconfirmed'
                },
                form: {
                    answer: 'testanswer',
                    captcha: 'testcaptcha'
                }
            }
        });

        initDeleteProcess()(dispatch, getState);
        expect(questionCheck).toBeCalled();
        expect(questionCheck).toBeCalledWith('testanswer');
    });
});
