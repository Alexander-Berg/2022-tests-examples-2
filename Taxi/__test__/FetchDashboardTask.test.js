const { FetchDashboardTaskV1 } = require('../FetchDashboardTask');
const { NoRequiredParametersError, NoEncryptKeyError } = require('../../../../errors');
const { CRYPTO_API, RAW_VALUE, ENCRYPTED_VALUE, ENCRYPT_KEY } = require('../../../../mocks/EncryptDecryptUtils');

const strategy = new FetchDashboardTaskV1(CRYPTO_API);
const {encryptKeyParameterName: KEY_PARAMETER} = strategy.options;

const TASKS = [
    {
        last_message: {
            text: ENCRYPTED_VALUE,
            created: '2021-09-08T11:11:38+0000',
            [KEY_PARAMETER]: ENCRYPT_KEY
        }
    },
    {
        last_message: {
            text: ENCRYPTED_VALUE,
            created: '2021-09-08T11:11:38+0000',
            [KEY_PARAMETER]: ENCRYPT_KEY,
            is_file: false
        }
    }
];
const VALID_RESPONSE_BODY = {
    tasks: TASKS,
    quest_timeout: 5000
};

const BODY_WITH_EMPTY_TASKS = {
    tasks: []
};

const BODY_WITH_PARTIALLY_FILLED_TASKS = {
    tasks: [{}, ...TASKS, {}]
};

const INVALID_TASKS = [
    {
        last_message: {
            text: ENCRYPTED_VALUE,
            created: '2021-09-08T11:11:38+0000'
        }
    },
    {
        last_message: {
            text: ENCRYPTED_VALUE,
            created: '2021-09-08T11:11:38+0000'
        }
    }
];

describe('decrypt', () => {
    test('decrypt tasks in body with valid parameters', async () => {
        const { tasks } = await strategy.decryptResponse(VALID_RESPONSE_BODY);

        for (const { last_message: { text, [KEY_PARAMETER]: key } } of tasks) {
            expect(text).toBe(RAW_VALUE);
            expect(key).toBeUndefined();
        }
    });

    test('decrypt tasks in empty body', () => {
        expect(async () =>
            await strategy.decryptResponse({})
        ).rejects.toThrow(NoRequiredParametersError);
    });

    test('decrypt tasks in body with empty tasks array', async () => {
        const { tasks } = await strategy.decryptResponse(BODY_WITH_EMPTY_TASKS);

        expect(tasks).toHaveLength(0);
    });

    test('decrypt tasks in body with partially filled tasks', async () => {
        const { tasks } = await strategy.decryptResponse(BODY_WITH_PARTIALLY_FILLED_TASKS);

        expect(tasks).toHaveLength(BODY_WITH_PARTIALLY_FILLED_TASKS.tasks.length);
    });
});

describe('encrypt', () => {
    test('returns body as is', async () => {
        const encryptedBody = await strategy.encryptRequest(VALID_RESPONSE_BODY);

        expect(encryptedBody).toEqual(VALID_RESPONSE_BODY);
    });
});

describe('prepare decrypt task', () => {
    test('method execute with invalid parameters', () => {
        expect(() => {
            strategy._getDataForDecrypt(INVALID_TASKS);
        }).toThrow(NoEncryptKeyError);
    });

    test('method execute with invalid parameters and throwWhenNoEncryptKeyInResponse:false', () => {
        const strategy = new FetchDashboardTaskV1({}, {throwWhenNoEncryptKeyInResponse: false});

        const prepareTasks = strategy._getDataForDecrypt(INVALID_TASKS);

        expect(prepareTasks).toEqual({});
    });
});
