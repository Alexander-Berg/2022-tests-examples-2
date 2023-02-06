const {AddMessageV2} = require('../AddMessage');
const {NoRequiredParametersError} = require('../../../../errors');
const {CRYPTO_API, ENCRYPT_KEY, RAW_VALUE, ENCRYPTED_VALUE} = require('../../../../mocks/EncryptDecryptUtils');

const strategy = new AddMessageV2(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const VALID_REQUEST_BODY = {
    message_id: 'fe17dfdc67c44d1dbbb7c700ddc1c419',
    message: RAW_VALUE,
    type: 'text',
    message_metadata: {
        attachments: []
    }
};

const VALID_REQUEST_BODY_CSAT = {
    type: 'csat',
    metadata: {
        csat_values: {
            questions: [
                {id: 'support_quality', value: { id: 'amazing'}},
                {id: 'support_quality', value: { id: 'good'}},
                {id: 'support_quality', value: { id: 'good'}},
                {id: 'leave_note', value: { comment: RAW_VALUE}},
                {id: 'leave_note'}
            ]
        }
    }
};

const BODY_WITHOUT_METADATA = {
    message_id: 'fe17dfdc67c44d1dbbb7c700ddc1c419',
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
        const { message, message_metadata: {[KEY_PARAMETER]: key}} = await strategy.encryptRequest(BODY_WITHOUT_METADATA);

        expect(message).toBe(ENCRYPTED_VALUE);
        expect(key).toBe(ENCRYPT_KEY);
    });

    test('encrypt message in empty body', () => {
        expect(async () => {
            await strategy.encryptRequest({});
        }).rejects.toThrow(NoRequiredParametersError);
    });

    test('encrypt CSAT in body with valid parameters', async () => {
        const encryptBody = await strategy.encryptRequest(VALID_REQUEST_BODY_CSAT);

        const validQuestions = VALID_REQUEST_BODY_CSAT.metadata.csat_values.questions;
        const {questions} = encryptBody.metadata.csat_values;

        questions.forEach((question, i) => {
            const {value} = question;
            const {comment, [KEY_PARAMETER]: key} = value || {};

            if (comment !== undefined) {
                expect(comment).toBe(ENCRYPTED_VALUE);
                expect(key).toBe(ENCRYPT_KEY);
            } else {
                expect(question).toEqual(validQuestions[i]);
            }
        });
    });
});

describe('encrypt CSAT', () => {
    test('method execute with empty body', async () => {
        const encryptCSAT = await strategy._encryptCSAT({});

        expect(encryptCSAT).toEqual({});
    });
});
