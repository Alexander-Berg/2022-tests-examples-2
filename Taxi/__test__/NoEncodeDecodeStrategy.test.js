const {NoEncodeDecodeStrategy} = require('../NoEncodeDecodeStrategy');
const {CRYPTO_API} = require('../../mocks/EncryptDecryptUtils');

const strategy = new NoEncodeDecodeStrategy(CRYPTO_API);

const BODY = {
    key: 'dfsdswe23dsxcs'
};

describe('encrypt', () => {
    test('returns body as is', async () => {
        const encryptedBody = await strategy.encryptRequest(BODY);

        expect(encryptedBody).toEqual(BODY);
    });
});

describe('decrypt', () => {
    test('returns body as is', async () => {
        const decryptedBody = await strategy.decryptResponse(BODY);

        expect(decryptedBody).toEqual(BODY);
    });
});
