import { createMooaDuck } from '../mooa';

describe('mooa reducer', () => {
    it('should append request to state', () => {
        const mooaDuck = createMooaDuck('mooa');
        expect(
            mooaDuck.reducer(
                {
                    requestLogs: [],
                },
                mooaDuck.actions.appendLogs([
                    {
                        method: 'GET',
                        status: 'success' as const,
                        url: 'http://example.com/test',
                        statusCode: 200,
                        requestHeaders: {},
                        responseHeaders: {},
                        requestBody: '',
                        type: 'request',
                    },
                ]),
            ),
        ).toEqual({
            requestLogs: [
                {
                    method: 'GET',
                    status: 'success',
                    url: 'http://example.com/test',
                    statusCode: 200,
                    requestHeaders: {},
                    responseHeaders: {},
                    requestBody: '',
                    type: 'request',
                },
            ],
        });
    });
});
