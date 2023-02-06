const {requestWithRetries} = require('../../../server/utils/requestWithRetries');

describe('Проверка корректной работы requestWithRetries', () => {
    function succcessRequestor(data) {
        return new Promise(resolve => {
            resolve(data);
        });
    }

    test('Должен вернуться корректный ответ', async () => {
        const response = await requestWithRetries({
            requestor: succcessRequestor,
            requestData: {ok: true},
        });

        expect(response).toEqual({ok: true});
    });

    const errorResponseData = {
        someReason: 'text',
        ok: false,
    };

    function errorRequestor() {
        return new Promise((resolve, reject) => {
            reject(errorResponseData);
        });
    }

    test('Должен корректно обработаться неверный ответ', async () => {
        try {
            await requestWithRetries({
                requestor: errorRequestor,
                requestData: {},
            });
        } catch (error) {
            expect(error).toEqual(errorResponseData);
        }
    });

    function validateHandlerRequestor(data) {
        return new Promise((resolve, reject) => {
            if (data.ok) {
                resolve(data);
            }

            reject(errorResponseData);
        });
    }

    test('Должен корректно примениться обработчик ошибок на неверный ответ', async () => {
        const response = await requestWithRetries({
            requestor: validateHandlerRequestor,
            requestData: {ok: false},
            validErrorHandler: (requestor, data, error) => {
                expect(error).toEqual(errorResponseData);

                data.ok = true;
                return requestor(data);
            },
        });

        expect(response).toEqual({ok: true});
    });
});
