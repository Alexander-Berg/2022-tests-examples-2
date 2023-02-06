import playCaptcha from '../playCaptcha';

describe('Action: playCaptcha', () => {
    it('should play captcha', () => {
        const playFn = jest.fn();
        const getState = () => ({
            captcha: {
                captchaSound: {
                    play: playFn
                }
            }
        });

        playCaptcha()(undefined, getState);

        expect(playFn).toBeCalled();
    });

    it('should ignore play captcha', () => {
        const getState = () => ({
            captcha: {
                captchaSound: {}
            }
        });

        playCaptcha()(undefined, getState);
    });
});
