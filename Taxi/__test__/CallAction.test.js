const {CallActionV1} = require('../CallAction');
const {CRYPTO_API, ENCRYPTED_VALUE, RAW_VALUE, ENCRYPT_KEY} = require('../../../../mocks/EncryptDecryptUtils');

const strategy = new CallActionV1(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const VALID_BODY = {
    comment: RAW_VALUE,
    macro_ids: [],
    themes: [],
    themes_tree: [],
    hidden_comment: 'Comment',
    selected_messages_id: [],
    request_id: '807d0813-b5b5-4af5-be5f-8e4833704708'
};

const BODY_WITHOUT_COMMENT = {
    selected_messages_id: [],
    request_id: '807d0813-b5b5-4af5-be5f-8e4833704708'
};

describe('encrypt', () => {
    test('encrypt action in body with valid parameters', async () => {
        const { comment, comment_metadata: {[KEY_PARAMETER]: key} } = await strategy.encryptRequest(VALID_BODY);

        expect(comment).toBe(ENCRYPTED_VALUE);
        expect(key).toBe(ENCRYPT_KEY);
    });

    test('encrypt action in body without comment', async () => {
        const encryptAction = await strategy.encryptRequest(BODY_WITHOUT_COMMENT);

        expect(encryptAction).toEqual(BODY_WITHOUT_COMMENT);
    });
});

describe('decrypt', () => {
    test('returns bosy as is', async () => {
        const decryptedResponse = await strategy.decryptResponse(VALID_BODY);

        expect(decryptedResponse).toEqual(VALID_BODY);
    });
});
