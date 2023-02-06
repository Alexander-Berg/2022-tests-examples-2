const BaseApi = require('../baseApi');
const got = require('got');

jest.mock('got');

const req = {
    headers: {},
    get: function (val) {
        return this.headers[val];
    }
};

describe('server api', () => {
    describe('BaseApi', () => {
        const responseData = {user: 'test'};

        test('createInstance должен создать инстанс api', () => {
            const api = BaseApi.createInstance({host: 'https://test.yandex.ru'});
            expect(api).toBeInstanceOf(BaseApi);
        });

        test('createInstance должен падать с ошибкой если указан неверный конфиг', () => {
            expect(() => {
                BaseApi.createInstance();
            }).toThrow();
        });

        test('Запрос к api проходит основные циклы', () => {
            const parse = jest.fn();
            const headerProcess = jest.fn();
            const postRequest = jest.fn();

            class ClientApi extends BaseApi {
                parse(response) {
                    parse(response);
                    return JSON.parse(response.body);
                }

                headerProcess(req) {
                    headerProcess(req);
                    return req;
                }

                postRequest(data) {
                    postRequest(data);
                    return data;
                }
            }

            const api = ClientApi.createInstance({host: 'test'});

            got.post.mockResolvedValue({
                statusCode: 200,
                body: JSON.stringify(responseData),
                headers: {'x-yarequestid': 1}
            });

            return api.post('/test', {id: 1}, req).then(data => {
                expect(parse).toBeCalled();
                expect(headerProcess).toBeCalled();
                expect(postRequest).toBeCalled();

                expect(data).toEqual(responseData);
            });
        });

        test('Ключ кеша формируется верно', () => {
            let cacheKey;

            class ClientApi extends BaseApi {
                buildCacheKey(...args) {
                    cacheKey = super.buildCacheKey(...args);

                    return cacheKey;
                }
            }
            const api = ClientApi.createInstance({host: 'test'}, {cache: true, ignoreKeys: ['id'], maxAge: 300});
            const responseData = {user: 'test'};

            got.post.mockResolvedValue({statusCode: 200, body: JSON.stringify(responseData)});

            return api.post('/test', {id: 1, lang: 'ru'}, req).then(() => {
                expect(cacheKey).toBe('test__ru');
            });
        });

        test('При наличия кеша повторного запроса не происходит', () => {
            let mockFn = jest.fn();

            const api = BaseApi.createInstance({host: 'test'}, {cache: true, ignoreKeys: ['id'], maxAge: 300});
            const responseData = {user: 'test'};

            got.post.mockImplementation(() => {
                mockFn();
                return Promise.resolve({statusCode: 200, body: JSON.stringify(responseData)});
            });

            return api
                .post('/test', {id: 1, lang: 'ru'}, req)
                .then(() => {
                    expect(mockFn.mock.calls.length).toBe(1);

                    return api.post('/test', {id: 1, lang: 'ru'}, req);
                })
                .then(() => {
                    expect(mockFn.mock.calls.length).toBe(1);
                });
        });
    });
});
