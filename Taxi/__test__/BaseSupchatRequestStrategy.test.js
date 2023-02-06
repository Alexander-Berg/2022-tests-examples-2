const { BaseSupchatRequestStrategy } = require('../BaseSupchatRequestStrategy');
const { NoRequiredParametersError, NoEncryptKeyError } = require('../../../../errors');
const { CRYPTO_API, RAW_VALUE, ENCRYPT_KEY, ENCRYPTED_VALUE } = require('../../../../mocks/EncryptDecryptUtils');
const { VALID_RESPONSE_QUESTIONS, createValidDecryptData, INVALID_RESPONSE_QUESTIONS } = require('../../../../mocks/csat');
const {
    NO_DECRYPT,
    HIDDEN_COMMENTS,
    ENCRYPT_HIDDEN_COMMENTS,
    createValidDataForDecrypt,
    ENCRYPT_INVALID_HIDDEN_COMMENTS
} = require('../../mocks/hiddenComments');

const strategy = new BaseSupchatRequestStrategy(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const MESSAGES = [
    {
        id: 'cfe905fb-89b1-4e3e-bb75-175762e2e99c',
        text: ENCRYPTED_VALUE,
        metadata: {
            ticket_subject: 'Ошибка «Нет доступных парков»',
            attachments: [],
            [KEY_PARAMETER]: ENCRYPT_KEY
        }
    },
    {
        id: 'fe18ea51-d821-4dae-8a38-f12b77d370a7',
        text: ENCRYPTED_VALUE,
        metadata: {
            attachments: [],
            [KEY_PARAMETER]: ENCRYPT_KEY
        }

    }
];

const VALID_RESPONSE_BODY = {
    id: '6077f15b80c095377d7ab90f',
    line: 'selfreg_driver_first',
    chat_messages: {
        messages: MESSAGES,
        total: 2,
        new_message_count: 0,
        newest_message_id: 'fe18ea51-d821-4dae-8a38-f12b77d370a7',
        metadata: {
            csat_values: {
                questions: [
                    { id: 'support_note', value: { id: 'goood'}},
                    { id: 'leave_note', value: { comment: ENCRYPTED_VALUE, [KEY_PARAMETER]: ENCRYPT_KEY}}
                ]
            }
        }
    }
};

const BODY_WITHOUT_MESSAGES = {
    chat_messages: {
        messages: []
    }
};

const BODY_WITH_PARTIAL_EMPTY_MESSAGE = {
    chat_messages: {
        messages: [{}, ...MESSAGES, {}]
    }
};

describe('decrypt', () => {
    test('decrypt messages in body with valid parameters', async () => {
        const {chat_messages: {messages, metadata}} = await strategy.decryptResponse(VALID_RESPONSE_BODY);
        const {questions} = metadata.csat_values;

        for (const question of questions) {
            const { value: {comment, id, [KEY_PARAMETER]: key}} = question;

            if (comment) {
                expect(comment).toBe(RAW_VALUE);
            } else {
                expect(id).toBeDefined();
            }

            expect(key).toBeUndefined();
        }

        for (const {text, metadata: {[KEY_PARAMETER]: key}} of messages) {
            expect(text).toBe(RAW_VALUE);
            expect(key).toBeUndefined();
        }
    });

    test('decrypt messages in empty body', () => {
        expect(async () => {
            await strategy.decryptResponse({});
        }).rejects.toThrow(NoRequiredParametersError);
    });

    test('decrypt messages in body with empty messages', async () => {
        const { chat_messages: {messages}} = await strategy.decryptResponse(BODY_WITHOUT_MESSAGES);

        expect(messages).toHaveLength(0);
    });

    test('decrypt messages in body with partial empty messages', async () => {
        const { chat_messages: {messages}} = await strategy.decryptResponse(BODY_WITH_PARTIAL_EMPTY_MESSAGE);

        expect(messages).toHaveLength(BODY_WITH_PARTIAL_EMPTY_MESSAGE.chat_messages.messages.length);
    });
});

describe('encrypt', () => {
    test('returns body as is', async () => {
        const ecnryptedBody = await strategy.encryptRequest(VALID_RESPONSE_BODY);

        expect(ecnryptedBody).toEqual(VALID_RESPONSE_BODY);
    });
});

describe('apply decrypt hidden comments', () => {
    test('method execute with valid parameters', () => {
        const dataForDecrypt = createValidDataForDecrypt(strategy._getEncryptDataKeyForHiddenComment.bind(strategy));
        const comments = strategy._applyDecryptedHiddenComments(HIDDEN_COMMENTS, dataForDecrypt);

        comments.forEach(({comment}, index) => {
            const decryptData = dataForDecrypt[strategy._getEncryptDataKeyForHiddenComment(index)];

            if (decryptData) {
                expect(comment).toBe(RAW_VALUE);
            } else {
                expect(comment).toBe(NO_DECRYPT);
            }
        });
    });
});

describe('get keys for decrypt from hidden comments', () => {
    test('method execute with valid parameters', () => {
        const prepareData = strategy._getDataForDecryptFromHiddenComments(ENCRYPT_HIDDEN_COMMENTS);

        HIDDEN_COMMENTS.forEach(({comment}, index) => {
            const { data, key} = prepareData[strategy._getEncryptDataKeyForHiddenComment(index)];

            expect(data).toBe(comment);
            expect(key).toBe(ENCRYPT_KEY);
        });
    });

    test('the method is executed without the necessary keys and throwWhenNoEncryptKeyInResponse: false', () => {
        const strategy = new BaseSupchatRequestStrategy(CRYPTO_API, {throwWhenNoEncryptKeyInResponse: false});
        const prepareData = strategy._getDataForDecryptFromHiddenComments(ENCRYPT_INVALID_HIDDEN_COMMENTS);

        ENCRYPT_HIDDEN_COMMENTS.forEach((_, index) => {
            const prepareComment = prepareData[strategy._getEncryptDataKeyForHiddenComment(index)];

            expect(prepareComment).toBeUndefined();
        });
    });

    test('the method is executed without the necessary keys and throwWhenNoEncryptKeyInResponse: true', () => {
        expect(() => {
            strategy._getDataForDecryptFromHiddenComments(ENCRYPT_INVALID_HIDDEN_COMMENTS);
        }).toThrow(NoEncryptKeyError);
    });
});

describe('apply decrypt csat', () => {
    test('method execute with valid parameters', () => {
        const decryptCSAT = strategy._applyDecryptedCSATQuestions(
            VALID_RESPONSE_QUESTIONS,
            createValidDecryptData(strategy._getEncryptDataKeyForCSATQuestionComment.bind(strategy))
        );

        decryptCSAT.forEach((csat, i) => {
            const {value: {comment, [KEY_PARAMETER]: key}} = csat;

            if (comment !== undefined) {
                expect(comment).toBe(RAW_VALUE);
            }

            expect(key).toBeUndefined();
        });
    });
});

describe('get keys for decrypt from CSAT', () => {
    test('method execute with valid parameters', () => {
        const prepareCSAT = strategy._getDataForDecryptFromCSAT(VALID_RESPONSE_QUESTIONS);

        expect(Object.keys(prepareCSAT)).toHaveLength(1);
    });

    test('method returned throw', () => {
        expect(() => {
            strategy._getDataForDecryptFromCSAT(INVALID_RESPONSE_QUESTIONS);
        }).toThrow(NoEncryptKeyError);
    });

    test('executing a method with the throwWhenNoEncryptKeyInResponse:false key', () => {
        const strategy = new BaseSupchatRequestStrategy({}, {throwWhenNoEncryptKeyInResponse: false});

        const prepareCSAT = strategy._getDataForDecryptFromCSAT(INVALID_RESPONSE_QUESTIONS);

        expect(prepareCSAT).toEqual({});
    });
});
