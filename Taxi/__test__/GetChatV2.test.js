const {GetChatV2} = require('../GetChat');
const {CRYPTO_API, ENCRYPT_KEY} = require('../../../../mocks/EncryptDecryptUtils');

const strategy = new GetChatV2(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const MOCK_MESSAGES = [
    {text: 'hello', body: 'hello', metadata: {[KEY_PARAMETER]: ENCRYPT_KEY}},
    {text: 'hello', body: 'hello', metadata: {[KEY_PARAMETER]: ENCRYPT_KEY}},
    {text: 'hello', body: 'hello', metadata: {[KEY_PARAMETER]: ENCRYPT_KEY}}
];
const VALID_BODY = {any_params: 'sdfsdfds', messages: MOCK_MESSAGES};

describe('ecnrypt', () => {
    test('encrypt message in body with valid parameters', async () => {
        const ecnryptedBody = await strategy.encryptRequest(VALID_BODY);

        expect(ecnryptedBody).toEqual(VALID_BODY);
    });
});
