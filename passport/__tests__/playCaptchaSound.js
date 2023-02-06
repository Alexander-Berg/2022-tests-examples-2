import {changeCaptchaPlayStatus} from '../';
import playCaptcha from '../playCaptcha';
import playCaptchaSound from '../playCaptchaSound';

jest.mock('../', () => ({
    changeCaptchaPlayStatus: jest.fn()
}));
jest.mock('../playCaptcha');

const dispatch = jest.fn();

describe('Action: playCaptchaSound', () => {
    beforeEach(() => {
        dispatch.mockClear();
        playCaptcha.mockClear();
        changeCaptchaPlayStatus.mockClear();
    });

    it('should play captcha', () => {
        const getState = () => ({
            captcha: {
                playing: false,
                introSound: 'introSound'
            }
        });

        playCaptchaSound()(dispatch, getState);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(2);
        expect(changeCaptchaPlayStatus).toBeCalled();
        expect(playCaptcha).toBeCalled();
    });

    it('should play captcha intro', () => {
        const playFn = jest.fn();
        const getState = () => ({
            captcha: {
                playing: false,
                introSound: {
                    play: playFn
                }
            }
        });

        playCaptchaSound(true)(dispatch, getState);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);
        expect(changeCaptchaPlayStatus).toBeCalled();
        expect(playCaptcha).not.toBeCalled();
        expect(playFn).toBeCalled();
    });

    it('should ignore playing', () => {
        const getState = () => ({
            captcha: {
                playing: true,
                introSound: 'introSound'
            }
        });

        playCaptchaSound()(dispatch, getState);

        expect(dispatch.mock.calls.length).toBe(0);
        expect(changeCaptchaPlayStatus).not.toBeCalled();
        expect(playCaptcha).not.toBeCalled();
    });

    it('should ignore play captcha intro', () => {
        const getState = () => ({
            captcha: {
                playing: false,
                introSound: {}
            }
        });

        playCaptchaSound(true)(dispatch, getState);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);
        expect(changeCaptchaPlayStatus).toBeCalled();
        expect(playCaptcha).not.toBeCalled();
    });
});
