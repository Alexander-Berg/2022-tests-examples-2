import { HTTPError, ApiHTTPError } from '..';

describe('HTTPError', () => {
    it('works with default params', () => {
        const error = new HTTPError(500, {});

        expect(error.getMessage()).toBe(
            'HTTPError: 500 Internal Server Error, Method: Unknown, Url: Unknown',
        );
    });

    it('properly generates message', () => {
        const error = new HTTPError(404, {
            method: 'GET',
            url: 'https://yandex.ru',
        });
        expect(error.getMessage()).toBe(
            'HTTPError: 404 Not Found, Method: GET, Url: https://yandex.ru',
        );
    });

    it('.serialize', () => {
        const error = new HTTPError(404, {
            method: 'GET',
            url: 'https://yandex.ru',
            headers: {
                a: '1',
                'X-Ya-Service-Ticket': 'qwerty',
                'X-Ya-User-Ticket': 'asdfgh',
            },
        });

        expect(error.serialize()).toMatchSnapshot();
    });

    it('.safeSerialize', () => {
        const error = new HTTPError(404, {
            method: 'GET',
            url: 'https://yandex.ru',
            headers: {
                a: '1',
                'X-Ya-Service-Ticket': 'qwerty',
                'X-Ya-User-Ticket': 'asdfgh',
            },
        });

        expect(error.safeSerialize()).toMatchSnapshot();
    });
});

describe('ApiHTTPError', () => {
    it('.safeSerialize', () => {
        const error = new ApiHTTPError(404, {
            method: 'GET',
            url: 'https://yandex.ru',
            headers: {
                a: '1',
                'X-Ya-Service-Ticket': 'qwerty',
                'X-Ya-User-Ticket': 'asdfgh',
            },
        });

        expect(error.safeSerialize()).toMatchSnapshot();
    });
});
