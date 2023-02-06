import destroyAudioCaptcha from '../destroyAudioCaptcha';

describe('Action: destroyAudioCaptcha', () => {
    it('should successfully unload sounds', () => {
        const introSoundUnloadFn = jest.fn();
        const captchaSoundUnloadFn = jest.fn();
        const getState = () => ({
            captcha: {
                introSound: {
                    unload: introSoundUnloadFn
                },
                captchaSound: {
                    unload: captchaSoundUnloadFn
                }
            }
        });

        destroyAudioCaptcha()(undefined, getState);

        expect(introSoundUnloadFn).toBeCalled();
        expect(captchaSoundUnloadFn).toBeCalled();
    });

    it('should ignore unload sounds for invalid sound objects', () => {
        const getState = () => ({
            captcha: {
                introSound: {},
                captchaSound: {}
            }
        });

        destroyAudioCaptcha()(undefined, getState);
    });
});
