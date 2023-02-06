import mapStateToProps from '../mapStateToProps';

describe('Components: CaptchaField.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            settings: {
                isNoTabletTouch: true,
                language: 'ru',
                env: {type: 'development'}
            },
            auth: {
                isCaptchaRequired: true,
                captchaError: 'captchaError',
                form: {
                    captcha_answer: 'captchaAnswer'
                }
            },
            captcha: {
                introSound: 'introSound',
                captchaSound: 'captchaSound',
                imageUrl: 'imageUrl',
                loading: 'loading',
                loadingAudio: 'loadingAudio',
                playing: 'playing',
                type: 'type',
                key: 'captchaKey'
            }
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            isNoTabletTouch: true,
            captchaAnswer: 'captchaAnswer',
            isCaptchaRequired: true,
            lang: 'ru',
            fieldError: '_AUTH_.Errors.internal',
            introSound: 'introSound',
            captchaSound: 'captchaSound',
            imageUrl: 'imageUrl',
            env: {type: 'development'},
            loading: 'loading',
            loadingAudio: 'loadingAudio',
            playing: 'playing',
            type: 'type',
            captchaKey: 'captchaKey',
            isAm: false
        });
    });

    it('should fallback props', () => {
        const state = {
            settings: {
                isNoTabletTouch: true,
                language: 'ru',
                env: {
                    type: 'development'
                }
            },
            auth: {
                isCaptchaRequired: true,
                captchaError: '',
                form: {
                    captcha_answer: 'captchaAnswer'
                }
            },
            captcha: {
                introSound: 'introSound',
                captchaSound: 'captchaSound',
                imageUrl: 'imageUrl',
                loading: 'loading',
                loadingAudio: 'loadingAudio',
                playing: 'playing',
                type: 'type',
                key: 'captchaKey'
            }
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            isNoTabletTouch: true,
            captchaAnswer: 'captchaAnswer',
            isCaptchaRequired: true,
            lang: 'ru',
            fieldError: null,
            env: {type: 'development'},
            introSound: 'introSound',
            captchaSound: 'captchaSound',
            imageUrl: 'imageUrl',
            loading: 'loading',
            loadingAudio: 'loadingAudio',
            playing: 'playing',
            type: 'type',
            captchaKey: 'captchaKey',
            isAm: false
        });
    });
});
