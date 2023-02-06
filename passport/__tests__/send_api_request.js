import sendApiRequest from '../send_api_request';
import checkCaptcha from '../check_captcha';

jest.mock('../check_captcha');

describe('Actions: sendApiRequest', () => {
    beforeEach(() => {
        checkCaptcha.mockImplementation(() => ({type: 'CAPTCHA_ACTION'}));
    });

    afterEach(() => {
        checkCaptcha.mockClear();
    });

    test('should call action creator with args', () => {
        const dispatch = jest.fn();
        const action = {type: 'SOME_ACTION'};
        const args = ['arg.1', 'arg.2'];
        const actionCreator = jest.fn(() => action);
        const getState = jest.fn(() => ({
            additionalDataRequest: {}
        }));

        sendApiRequest(actionCreator, args[0], args[1])(dispatch, getState);

        expect(dispatch).toBeCalledWith(action);
        expect(actionCreator).toBeCalledWith(args[0], args[1]);
    });

    test('should call check captcha action and pass action creator with args', () => {
        const dispatch = jest.fn();
        const action = {type: 'CAPTCHA_ACTION'};
        const args = ['arg.1', 'arg.2'];
        const actionCreator = jest.fn(() => action);
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                isCaptchaRequired: true
            }
        }));

        sendApiRequest(actionCreator, args[0], args[1])(dispatch, getState);

        expect(dispatch).toBeCalledWith(action);
        expect(checkCaptcha).toBeCalledWith(actionCreator, args);
    });
});
