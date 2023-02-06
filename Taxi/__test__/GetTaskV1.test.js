const {GetTaskV1} = require('../GetTask');
const {CRYPTO_API, RAW_VALUE, ENCRYPTED_VALUE, ENCRYPT_KEY} = require('../../../../../mocks/EncryptDecryptUtils');

const strategy = new GetTaskV1(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const VALID_BODY = {
    created: '2021-08-30T09:33:09+0000',
    hidden_comments: [],
    sip_settings: {
        allow_call: false,
        allow_call_any_number: false
    },
    chat_messages: {
        messages: [
            {
                text: ENCRYPTED_VALUE,
                metadata: {
                    [KEY_PARAMETER]: ENCRYPT_KEY,
                    country: 'ru'
                },
                sender: {
                    role: 'client',
                    sender_type: 'client'
                }
            },
            {
                text: ENCRYPTED_VALUE,
                metadata: {
                    [KEY_PARAMETER]: ENCRYPT_KEY,
                    country: 'ru'
                },
                sender: {
                    role: 'client',
                    sender_type: 'client'
                }
            },
            {
                text: ENCRYPTED_VALUE,
                metadata: {
                    [KEY_PARAMETER]: ENCRYPT_KEY,
                    created: '2021-08-31T11:58:51+0000'
                },
                sender: {
                    role: 'support',
                    sender_type: 'support'
                }
            }
        ]
    }
};

describe('decrypt', () => {
    test('decrypt data in body with valid parameters', async () => {
        const {chat_messages} = await strategy.decryptResponse(VALID_BODY);

        for (const {metadata, text} of chat_messages.messages) {
            expect(text).toEqual(RAW_VALUE);
            expect(metadata[KEY_PARAMETER]).toBeUndefined();
        }

        expect(chat_messages.messages).not.toHaveLength(0);
    });

    test('decrypt data in empty body', () => {
        expect(async () => {
            await strategy.decryptResponse({});
        }).rejects.toThrow();
    });
});
