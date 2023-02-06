import { mooa as reducer } from '../mooa';
import * as actions from '../../actions/mooa';

describe('mooa reducer', () => {
    it('should append request to state', () => {
        expect(
            reducer(
                {
                    requestLogs: [],
                    usersMeta: [],
                    campaignsMeta: [],
                },
                actions.appendRequestLogs([
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
            usersMeta: [],
            campaignsMeta: [],
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
