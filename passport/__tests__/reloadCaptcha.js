import getCaptcha from '../getCaptcha';
import changeCaptchaAudio from '../changeCaptchaAudio';
import reloadCaptcha from '../reloadCaptcha';

const dispatch = jest.fn();

jest.mock('../getCaptcha');
jest.mock('../changeCaptchaAudio');

describe('Action: reloadCaptcha', () => {
    beforeEach(() => {
        dispatch.mockClear();
        getCaptcha.mockClear();
        changeCaptchaAudio.mockClear();
    });

    it('should get captcha', () => {
        const getState = () => ({
            captcha: {
                type: 'text'
            }
        });

        reloadCaptcha()(dispatch, getState);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);
        expect(getCaptcha).toBeCalled();
        expect(changeCaptchaAudio).not.toBeCalled();
    });

    it('should change audio captcha', () => {
        const getState = () => ({
            captcha: {
                type: 'audio'
            }
        });

        reloadCaptcha()(dispatch, getState);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);
        expect(getCaptcha).not.toBeCalled();
        expect(changeCaptchaAudio).toBeCalled();
    });
});
