import sendApiRequest from '../sendApiRequest';
import checkCaptcha from '../checkCaptcha';

jest.mock('../checkCaptcha');

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
            auth: {}
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
            auth: {
                isCaptchaRequired: true
            }
        }));

        sendApiRequest(actionCreator, args[0], args[1])(dispatch, getState);

        expect(dispatch).toBeCalledWith(action);
        expect(checkCaptcha).toBeCalledWith({action: actionCreator, actionArguments: args});
    });
});
