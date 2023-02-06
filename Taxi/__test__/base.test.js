import axios from 'axios';
import BaseAPI from '../base';

jest.mock('axios');

describe('base api', () => {
    let api;

    beforeEach(() => {
        api = new BaseAPI('/api');
    });

    afterEach(() => {
        axios.mockClear();
    });

    it('should be throw error, then no pathname', () => {
        expect(createInstanceAPIWithoutPathname).toThrow();
        expect(createInstanceAPI).not.toThrow();
    });

    it('should be return response', () => {
        const responseData = {data: 'value'};
        axios.mockResolvedValue(responseData);

        return api.get('/some').then(response => {
            expect(response).toEqual(responseData);
        });
    });

    it('should be throw object with error and request', () => {
        const request = {}; // nodejs request
        const errorData = {status: 403, statusText: 'Forbiden', data: {message: 'invalid'}};
        axios.mockRejectedValue(errorData);

        return api.get('/some', {}, request).catch(({error, req}) => {
            expect(error).not.toBeUndefined();
            expect(req).not.toBeUndefined();
            expect(req).toEqual(req);
            expect(error).toEqual(errorData);
        });
    });

    it('should be retry when error and `meta.retry` equal `true`', () => {
        const SUCCESS = 'SUCCESS';
        const ERROR = {status: 500, data: {message: 'shit happens'}};

        axios.mockRejectedValueOnce(ERROR).mockResolvedValue(SUCCESS);

        function repeatMiddleware({request}, meta) {
            request.catch(() => {
                if (meta.retryCount === 0) {
                    meta.retry = true;
                }
            });
        }

        api.registerMiddleware('response', repeatMiddleware, 'repeatMiddleware');

        return api.get('/some').then(value => {
            expect(value).toEqual(SUCCESS);
            expect(axios.mock.calls.length).toEqual(2);
        });
    });

    it('should be normalize endpoint', () => {
        expect(api._getEndpoint('/some')).toEqual('/api/some/');
        expect(api._getEndpoint('some')).toEqual('/api/some/');
        expect(api._getEndpoint('/some/')).toEqual('/api/some/');
        expect(new BaseAPI('/api')._getEndpoint('some')).toEqual('/api/some/');
        expect(new BaseAPI('https://api-host.yandex.net')._getEndpoint('some')).toEqual(
            'https://api-host.yandex.net/some/'
        );
    });

    it('should be register request middleware once', () => {
        const params = {
            endpoint: '/some',
            options: {
                params: {
                    param1: 'value1'
                }
            }
        };
        const requestHook = jest.fn();

        api.registerMiddleware('request', requestHook, 'requestHook');
        api.registerMiddleware('request', requestHook, 'requestHook');

        return api.get(params.endpoint, params.options).then(() => {
            expect(requestHook.mock.calls.length).toBe(1);

            const calledParams = requestHook.mock.calls[0][0];
            expect(calledParams.options.params).toEqual(params.options.params);
            expect(calledParams.endpoint).toEqual(api._getEndpoint(params.endpoint));
        });
    });

    it('should be register response middleware once', () => {
        const response = {data: 'value'};

        axios.mockResolvedValue(response);

        const responseHook = jest.fn();
        responseHook.mockResolvedValue();

        api.registerMiddleware('response', responseHook, 'responseHook');
        api.registerMiddleware('response', responseHook, 'responseHook');

        return api.get('/some').then(() => {
            expect(responseHook.mock.calls.length).toBe(1);

            return responseHook.mock.calls[0][0].request.then(data => {
                expect(data).toEqual(response);
            });
        });
    });
});

function createInstanceAPI() {
    return new BaseAPI('/api');
}

function createInstanceAPIWithoutPathname() {
    return new BaseAPI();
}
