const {BaseStrategy} = require('../BaseStrategy');
const {CRYPTO_API} = require('../../mocks/EncryptDecryptUtils');
const {INVALID_MESSAGES_WITHOUT_KEY} = require('../../mocks/messages');
const {NoRequiredParametersError, NoEncryptKeyError} = require('../../errors');

const baseStrategy = new BaseStrategy(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = baseStrategy.options;

const VALID_FUNCTION = body => body;

describe('withRequiredParametersCheck', () => {
    const BODY = {type: 'text', message: 'sdasdawxq'};

    test('defines as expected', () => {
        const decoratedFunction = baseStrategy.withRequiredParametersCheck(VALID_FUNCTION, ['type', 'message']);
        const body = decoratedFunction(BODY);

        expect(body).toEqual(BODY);
    });

    test('should return a NoRequiredParametersError', () => {
        expect(() =>
            baseStrategy.withRequiredParametersCheck(VALID_FUNCTION, ['type', 'message'])()
        ).toThrow(NoRequiredParametersError);
    });

    test('should return empty object', () => {
        const decoratedFunction = baseStrategy.withDecryptParametersCheck(VALID_FUNCTION);

        const result = decoratedFunction({});

        expect(result).toEqual({});
    });
});

describe('with decrypt parameters check', () => {
    const VALID_FN = message => message;

    const withDecoratedFn = baseStrategy.withDecryptParametersCheck(
        VALID_FN,
        'text',
        `metadata.${KEY_PARAMETER}`
    );

    const VALID_BODY = {
        text: 'sadscwecsd',
        metadata: {
            [KEY_PARAMETER]: 'Asce32WBcaSc'
        }
    };

    const BODY_WITHOUT_ENCRYPT_KEY = {
        text: 'sadscwecsd',
        metadata: {}
    };

    const BODY_WITHOUT_TEXT = {
        metadata: {
            [KEY_PARAMETER]: 'asc#CAScaws'
        }
    };

    const BODY_WITHOUT_ALL_IMPORTANT_KEYS = {
        uuid: 'sceses-sdqwqwdqc-scdw42342dw-22323',
        createAd: '2021'
    };

    test('defines as expected', () => {
        const handledBody = withDecoratedFn(VALID_BODY);

        expect(handledBody).toEqual(VALID_BODY);
    });

    test('body without encrypt key, should return a NoEncryptKeyError', () => {
        expect(() => {
            withDecoratedFn(BODY_WITHOUT_ENCRYPT_KEY);
        }).toThrow(NoEncryptKeyError);
    });

    test('body without text, should return body', () => {
        const handledBody = withDecoratedFn(BODY_WITHOUT_TEXT);

        expect(handledBody).toEqual(BODY_WITHOUT_TEXT);
    });

    test('body without all important keys, should return body', () => {
        const handledBody = withDecoratedFn(BODY_WITHOUT_ALL_IMPORTANT_KEYS);

        expect(handledBody).toEqual(BODY_WITHOUT_ALL_IMPORTANT_KEYS);
    });

    test('defines as expected with throwWhenNoEncryptKeyInResponse: false', () => {
        const baseStrategy = new BaseStrategy({}, { throwWhenNoEncryptKeyInResponse: false});

        const withDecoratedFn = baseStrategy.withDecryptParametersCheck(
            VALID_FN,
            'text',
            `metadata.${KEY_PARAMETER}`
        );

        const result = withDecoratedFn({text: 'hello'});

        expect(result).toEqual({text: 'hello'});
    });
});

describe('ecnrypt message', () => {
    test('encrypt message in body without text parameters', async () => {
        const MESSAGE = { id: 123 };
        const encryptMessage = await baseStrategy._encryptMessage(MESSAGE);

        expect(encryptMessage).toEqual(MESSAGE);
    });
});

describe('throw when no encrypt key in response', () => {
    test('expect to return false key', () => {
        const {throwWhenNoEncryptKeyInResponse} = new BaseStrategy({}).options;

        expect(throwWhenNoEncryptKeyInResponse).toBe(true);
    });

    test('expect to return true key', () => {
        const {throwWhenNoEncryptKeyInResponse} = new BaseStrategy({}, {throwWhenNoEncryptKeyInResponse: false}).options;

        expect(throwWhenNoEncryptKeyInResponse).toBe(false);
    });
});

describe('get data for decrypt from messages', () => {
    const strategy = new BaseStrategy({}, {throwWhenNoEncryptKeyInResponse: false});

    test('return keys with ', () => {
        const prepareMessages = strategy._getDataForDecryptFromMessages(INVALID_MESSAGES_WITHOUT_KEY);

        expect(prepareMessages).toEqual({});
    });
});
