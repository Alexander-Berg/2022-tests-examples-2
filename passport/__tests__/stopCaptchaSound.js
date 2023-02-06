import {changeCaptchaPlayStatus} from '../';
import stopCaptchaSound from '../stopCaptchaSound';

jest.mock('../', () => ({
    changeCaptchaPlayStatus: jest.fn()
}));

const dispatch = jest.fn();

describe('Action: stopCaptchaSound', () => {
    beforeEach(() => {
        dispatch.mockClear();
        changeCaptchaPlayStatus.mockClear();
    });

    it('should stop sounds', () => {
        const introSoundStopFn = jest.fn();
        const captchaSoundStopFn = jest.fn();
        const getState = () => ({
            captcha: {
                introSound: {
                    stop: introSoundStopFn
                },
                captchaSound: {
                    stop: captchaSoundStopFn
                }
            }
        });

        stopCaptchaSound()(dispatch, getState);

        expect(dispatch).toBeCalled();
        expect(changeCaptchaPlayStatus).toBeCalled();
        expect(introSoundStopFn).toBeCalled();
        expect(captchaSoundStopFn).toBeCalled();
    });

    it('should ignore stop sounds', () => {
        const getState = () => ({
            captcha: {
                introSound: {},
                captchaSound: {}
            }
        });

        stopCaptchaSound()(dispatch, getState);

        expect(dispatch).toBeCalled();
        expect(changeCaptchaPlayStatus).toBeCalled();
    });
});
