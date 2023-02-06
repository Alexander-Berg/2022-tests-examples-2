const { CreateTaskChatV2 } = require('../CreateTaskChat');
const { NoRequiredParametersError } = require('../../../../errors');
const { CRYPTO_API, ENCRYPTED_VALUE, RAW_VALUE, ENCRYPT_KEY } = require('../../../../mocks/EncryptDecryptUtils');

const strategy = new CreateTaskChatV2(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const VALID_BODY = {
    platform: 'yandex',
    user_phone: '+78005553535',
    order_id: '1233213',
    message: RAW_VALUE,
    status: 'new',
    request_id: '74cecd05-ed01-412d-b0db-1bdd4168af21'
};

const BODY_WITHOUT_MESSAGE = {
    platform: 'yandex',
    user_phone: '+78005553535',
    order_id: '1233213',
    status: 'new',
    request_id: '74cecd05-ed01-412d-b0db-1bdd4168af21'
};

describe('encrypt', () => {
    test('encrypt task in body with valid parameters', async () => {
        const { message, message_metadata } = await strategy.encryptRequest(VALID_BODY);
        const {[KEY_PARAMETER]: key} = message_metadata || {};

        expect(message).toBe(ENCRYPTED_VALUE);
        expect(key).toBe(ENCRYPT_KEY);
    });

    test('encrypt task in body without message', async () => {
        expect(async () =>
            await strategy.encryptRequest(BODY_WITHOUT_MESSAGE)
        ).rejects.toThrow(NoRequiredParametersError);
    });
});

describe('decrypt', () => {
    test('returns body as is', async () => {
        const decryptedBody = await strategy.decryptResponse(VALID_BODY);

        expect(decryptedBody).toEqual(VALID_BODY);
    });
});
