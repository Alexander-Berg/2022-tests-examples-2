const {GetTaskForSelectedLinesV1} = require('../GetTaskForSelectedLines');
const {RAW_VALUE, CRYPTO_API, ENCRYPT_KEY, ENCRYPTED_VALUE} = require('../../../../../mocks/EncryptDecryptUtils');

const strategy = new GetTaskForSelectedLinesV1(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const VALID_BODY = {
    id: '612ca5d506d38e7e321b9284',
    line: 'eda_online_2',
    chat_messages: {
        messages: [
            {
                text: ENCRYPTED_VALUE,
                metadata: {
                    attachments: [],
                    [KEY_PARAMETER]: ENCRYPT_KEY,
                    ticket_subject: 'Баллы и кешбэк'
                },
                sender: {
                    role: 'client',
                    sender_type: 'client'
                }
            },
            {
                text: ENCRYPTED_VALUE,
                metadata: {
                    [KEY_PARAMETER]: ENCRYPT_KEY
                },
                sender: {
                    role: 'client',
                    sender_type: 'client'
                }
            },
            {
                text: ENCRYPTED_VALUE,
                metadata: {
                    [KEY_PARAMETER]: ENCRYPT_KEY
                },
                sender: {
                    role: 'support',
                    sender_type: 'support'
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
            }
        ]
    }
};

describe('decrypt', () => {
    test('decrypt messages in body with valid parameters', async () => {
        const {chat_messages: { messages }} = await strategy.decryptResponse(VALID_BODY);

        for (const {text, metadata} of messages) {
            expect(text)
                .toBe(RAW_VALUE);

            expect(metadata[KEY_PARAMETER])
                .toBeUndefined();
        }

        expect(messages).not.toHaveLength(0);
    });

    test('decrypt messages in empty body', () => {
        expect(async () => {
            await strategy.decryptResponse({});
        }).rejects.toThrow();
    });
});
