import {
    getAudioCaptchaFail,
    loadCaptcha,
    getCaptchaFail,
    getAudioCaptcha,
    changeCaptchaPlayStatus,
    getAudioCaptchaSuccess,
    getImageCaptchaSuccess,
    changeCaptchaType,
    clearCaptchaProps
} from '../';

describe('Captcha Actions', () => {
    it('should handle GET_AUDIO_CAPTCHA_FAIL action', () => {
        const result = getAudioCaptchaFail('error');

        expect(result).toEqual({
            type: 'GET_AUDIO_CAPTCHA_FAIL',
            error: 'error'
        });
    });

    it('should handle LOAD_CAPTCHA action', () => {
        const result = loadCaptcha();

        expect(result).toEqual({
            type: 'LOAD_CAPTCHA'
        });
    });

    it('should handle GET_AUDIO_CAPTCHA action', () => {
        const result = getAudioCaptcha();

        expect(result).toEqual({
            type: 'GET_AUDIO_CAPTCHA'
        });
    });

    it('should handle GET_CAPTCHA_FAIL action', () => {
        const result = getCaptchaFail('error');

        expect(result).toEqual({
            type: 'GET_CAPTCHA_FAIL',
            error: 'error'
        });
    });

    it('should handle CHANGE_CAPTCHA_PLAY_STATUS action', () => {
        const result = changeCaptchaPlayStatus(true);

        expect(result).toEqual({
            type: 'CHANGE_CAPTCHA_PLAY_STATUS',
            playing: true
        });
    });

    it('should handle GET_AUDIO_CAPTCHA_SUCCESS action', () => {
        const key = 'key';
        const introSound = 'introSound';
        const captchaSound = 'captchaSound';

        let result = getAudioCaptchaSuccess(key, introSound, captchaSound);

        expect(result).toEqual({
            type: 'GET_AUDIO_CAPTCHA_SUCCESS',
            key,
            introSound,
            captchaSound
        });

        result = getAudioCaptchaSuccess(key, false, captchaSound);

        expect(result).toEqual({
            type: 'GET_AUDIO_CAPTCHA_SUCCESS',
            key,
            captchaSound
        });
    });

    it('should handle GET_IMAGE_CAPTCHA_SUCCESS action', () => {
        const key = 'key';
        const imageUrl = 'imageUrl';
        const result = getImageCaptchaSuccess(key, imageUrl);

        expect(result).toEqual({
            type: 'GET_IMAGE_CAPTCHA_SUCCESS',
            key,
            imageUrl
        });
    });

    it('should handle CHANGE_CAPTCHA_TYPE action', () => {
        const result = changeCaptchaType();

        expect(result).toEqual({
            type: 'CHANGE_CAPTCHA_TYPE'
        });
    });

    it('should handle CLEAR_CAPTCHA_PROPS action', () => {
        const result = clearCaptchaProps();

        expect(result).toEqual({
            type: 'CLEAR_CAPTCHA_PROPS'
        });
    });
});
