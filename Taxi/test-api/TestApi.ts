import {ClientError, ServerError} from 'common/isomorphic/errors';

export default class TestApi {
    public static testKnownErrorRequest() {
        return Promise.reject<Error>(new Error('Known error'));
    }

    public static testUnknownErrorRequest() {
        return Promise.reject<Error>(new Error('Unknown error'));
    }

    public static testClient404ErrorRequest() {
        return Promise.reject<ClientError>(new ClientError('Some client 404 error', '404'));
    }

    public static testClient403ErrorRequest() {
        return Promise.reject<ClientError>(new ClientError('Some client 403 error', '403'));
    }

    public static testServer500ErrorRequest() {
        return Promise.reject<ServerError>(new ServerError('Some server error', {
            originalError: {
                name: 'errName',
                message: 'Something happened with server',
                code: '500',
                config: {},
                isAxiosError: false,
                toJSON: () => ({})
            }
        }));
    }
}
