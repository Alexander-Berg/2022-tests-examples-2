const { BaseHelpRequestStrategy } = require('../BaseHelpRequestStrategy');
const { CRYPTO_API, RAW_VALUE, ENCRYPTED_VALUE, ENCRYPT_KEY } = require('../../../mocks/EncryptDecryptUtils');
const { NoRequiredParametersError, NoEncryptKeyError } = require('../../../errors');

const strategy = new BaseHelpRequestStrategy(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const VALID_RESPONSE_BODY = {
    messages: [
        {
            text: ENCRYPTED_VALUE,
            body: ENCRYPTED_VALUE,
            metadata: {
                [KEY_PARAMETER]: ENCRYPT_KEY
            }
        },
        {
            text: ENCRYPTED_VALUE,
            body: ENCRYPTED_VALUE,
            metadata: {
                [KEY_PARAMETER]: ENCRYPT_KEY
            }
        },
        {
            text: ENCRYPTED_VALUE,
            body: ENCRYPTED_VALUE,
            metadata: {
                [KEY_PARAMETER]: ENCRYPT_KEY
            }
        }
    ],
    participants: []
};

const INVALID_BODY_WITHOUT_KEY = {
    messages: [
        { text: 'asdas' }
    ]
};

const INVALID_BODY_EMPTY_MESSAGE = {
    messages: [
        { id: 2, type: 'text' },
        { id: 23421, type: 'text' }
    ]
};

const INVALID_BODY_UNDEFINED_TEXT = {
    messages: [
        { id: 2, type: 'text', metadata: { [KEY_PARAMETER]: ENCRYPT_KEY } },
        { id: 23421, type: 'text', metadata: { [KEY_PARAMETER]: ENCRYPT_KEY } }
    ]
};

describe('decrypt', () => {
    test('decrypt messages in body with valid parameters', async () => {
        const { messages } = await strategy.decryptResponse(VALID_RESPONSE_BODY);

        for (const { text, body, metadata: { [KEY_PARAMETER]: key } } of messages) {
            expect(text).toBe(RAW_VALUE);
            expect(body).toBe(RAW_VALUE);
            expect(key).toBeUndefined();
        }
    });

    test('decrypt messages in empty body', async () => {
        expect(async () => {
            await strategy.decryptResponse({});
        }).rejects.toThrow(NoRequiredParametersError);
    });

    test('decrypt messages in body without encrypt keys', async () => {
        expect(async () => {
            await strategy.decryptResponse(INVALID_BODY_WITHOUT_KEY);
        }).rejects.toThrow(NoEncryptKeyError);
    });

    test('decrypt messages without text and encrypt keys', async () => {
        const { messages } = await strategy.decryptResponse(INVALID_BODY_EMPTY_MESSAGE);

        for (const { text, metadata } of messages) {
            const encryptKey = metadata && metadata[KEY_PARAMETER];

            expect(text).toBeUndefined();
            expect(encryptKey).toBeUndefined();
        }
    });

    test('decrypt messages in body without text', async () => {
        const { messages } = await strategy.decryptResponse(INVALID_BODY_UNDEFINED_TEXT);

        for (const { text, metadata } of messages) {
            const encryptKey = metadata && metadata[KEY_PARAMETER];

            expect(text).toBeUndefined();
            expect(encryptKey).toBeUndefined();
        }
    });
});
