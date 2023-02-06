const {GetUserMessagesV1} = require('../GetUserMessages');
const {CRYPTO_API, ENCRYPT_KEY} = require('../../../../mocks/EncryptDecryptUtils');

const strategy = new GetUserMessagesV1(CRYPTO_API);
const {KEY_PARAMETER} = strategy;

const VALID_REQUEST_BODY = {
    messages: [
        {
            text: 'sdasdasda',
            body: 'sdasdasda',
            metadata: {
                [KEY_PARAMETER]: ENCRYPT_KEY
            }
        }
    ]
};

describe('encrypt', () => {
    test('returns body as is', async () => {
        const encryptBody = await strategy.encryptRequest(VALID_REQUEST_BODY);

        expect(encryptBody).toEqual(VALID_REQUEST_BODY);
    });
});
