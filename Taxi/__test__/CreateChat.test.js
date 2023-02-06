const {CreateChatV2} = require('../CreateChat');
const { NoRequiredParametersError } = require('../../../../errors');
const {CRYPTO_API, ENCRYPTED_VALUE, ENCRYPT_KEY, RAW_VALUE} = require('../../../../mocks/EncryptDecryptUtils');

const strategy = new CreateChatV2(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const VALID_REQUEST_BODY = {
    message_id: 'e8a1a56538ab4808868c15d4283a579c',
    message: RAW_VALUE,
    type: 'text',
    message_metadata: {attachments: []}
};

const BODY_WITHOUT_METADATA = {
    message_id: 'e8a1a56538ab4808868c15d4283a579c',
    message: RAW_VALUE,
    type: 'text'
};

describe('encrypt', () => {
    test('encrypt message in body with message_metadata', async () => {
        const {message, message_metadata: {[KEY_PARAMETER]: key}} = await strategy.encryptRequest(VALID_REQUEST_BODY);

        expect(message).toBe(ENCRYPTED_VALUE);
        expect(key).toBe(ENCRYPT_KEY);
    });

    test('encrypt message in body without message_metadata', async () => {
        const {message, message_metadata: {[KEY_PARAMETER]: key}} = await strategy.encryptRequest(BODY_WITHOUT_METADATA);

        expect(message).toBe(ENCRYPTED_VALUE);
        expect(key).toBe(ENCRYPT_KEY);
    });

    test('emcrypt message in empty body', () => {
        expect(async () => {
            await strategy.encryptRequest({});
        }).rejects.toThrow(NoRequiredParametersError);
    });
});
