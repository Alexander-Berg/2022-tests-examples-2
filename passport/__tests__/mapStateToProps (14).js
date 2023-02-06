import {mapStateToProps} from '../mapStateToProps';

jest.mock('@blocks/authv2/errors', () => ({
    'captcha.required': 'SomeTextKey',
    global: 'globalErrorTextKey'
}));

describe('@blocks/authv2/components/MagicBookPage/mapStateToProps', () => {
    it.each([
        [{auth: {magicCSRF: 'asd'}, settings: {}}, 'csrfToken', 'asd'],
        [{auth: {}, settings: {}}, 'csrfToken', undefined],
        [{auth: {isCaptchaRequired: true}, settings: {}}, 'isCaptchaRequired', true],
        [{auth: {}, settings: {}}, 'isCaptchaRequired', undefined],
        [{auth: {magicError: 'captcha.required'}, settings: {}}, 'fieldError', 'SomeTextKey'],
        [{auth: {magicError: 'newError'}, settings: {}}, 'fieldError', 'globalErrorTextKey'],
        [{auth: {}, settings: {}}, 'fieldError', null],
        [{auth: {processedAccount: {allowed_auth_methods: ['magic', 'otp']}}, settings: {}}, 'magicIcon', 'yandexKey'],
        [{auth: {processedAccount: {allowed_auth_methods: ['magic']}}, settings: {}}, 'magicIcon', 'yandex3-ru'],
        [{auth: {processedAccount: {allowed_auth_methods: ['otp']}}, settings: {}}, 'magicIcon', 'yandex3-ru'],
        [{auth: {processedAccount: {allowed_auth_methods: []}}, settings: {}}, 'magicIcon', 'yandex3-ru'],
        [{auth: {processedAccount: {}}, settings: {}}, 'magicIcon', 'yandex3-ru'],
        [{auth: {}, settings: {language: 'ru'}}, 'magicIcon', 'yandex3-ru'],
        [{auth: {}, settings: {language: 'uk'}}, 'magicIcon', 'yandex3-ru'],
        [{auth: {}, settings: {}}, 'magicIcon', 'yandex3-ru'],
        [{auth: {}, settings: {language: 'en'}}, 'magicIcon', 'yandex3-en'],
        [{auth: {magicTrack: 'qwe'}, settings: {}}, 'trackId', 'qwe']
    ])('should return correct props on state: %o with prop: %s with value: %s', (state, propName, expected) => {
        expect(mapStateToProps(state)[propName]).toEqual(expected);
    });
});
