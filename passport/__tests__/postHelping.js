jest.mock('@blocks/api', () => ({
    request: jest.fn()
}));

import {setAliceHelpingState} from '../actions/actions';
import {postHelping} from '../api';
import * as api from '@blocks/api';

describe('thunk postHelping', () => {
    const isEnabledHelping = true;
    const doneResult = {
        status: 'ok',
        helping: isEnabledHelping
    };
    const csrf = 'csrf';
    const uid = 'uid';
    const track_id = 'track_id';
    const getState = jest.fn(() => ({
        common: {
            csrf: csrf,
            uid: uid,
            track_id: track_id
        }
    }));
    const dispatch = jest.fn();

    const mockApi = ({success = true, doneResult: rewriteDoneResult = null} = {}) => {
        api.request.mockImplementation(() => {
            const FakeApi = function() {
                this.done = function(fn) {
                    if (success) {
                        const result = Object.assign({}, rewriteDoneResult || doneResult);

                        fn(result);
                    }
                    return this;
                };

                this.fail = function(fn) {
                    if (!success) {
                        fn();
                    }
                    return this;
                };
            };

            return new FakeApi();
        });
    };

    beforeEach(() => {
        mockApi();
    });

    afterEach(() => {
        api.request.mockClear();
        getState.mockClear();
        dispatch.mockClear();
    });

    it('Store changes immediately', async () => {
        api.request.mockImplementationOnce(() => {
            expect(dispatch.mock.calls.length).toEqual(1);
            expect(dispatch.mock.calls[0][0]).toEqual(setAliceHelpingState(isEnabledHelping));
            return {
                done: () => ({
                    fail: () => {}
                })
            };
        });
        postHelping(isEnabledHelping)(dispatch, getState);
    });

    it('Rollback client state after API request is failed', () => {
        mockApi({success: false});
        postHelping(isEnabledHelping)(dispatch, getState);
        const helpingStateAction = setAliceHelpingState(isEnabledHelping);
        const rollbackHelpingStateAction = setAliceHelpingState(!isEnabledHelping);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls[0][0]).toEqual(helpingStateAction);
        expect(api.request).toBeCalled();
        expect(dispatch.mock.calls[1][0]).toEqual(rollbackHelpingStateAction);
    });

    it('Rollback client state after API request answered "status" !== "ok"', () => {
        const rewriteApiResponse = {
            // no "status" key
            helpingEnabled: isEnabledHelping
        };

        mockApi({success: true, doneResult: rewriteApiResponse});
        postHelping(isEnabledHelping)(dispatch, getState);
        const helpingStateAction = setAliceHelpingState(isEnabledHelping);
        const rollbackHelpingStateAction = setAliceHelpingState(!isEnabledHelping);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls[0][0]).toEqual(helpingStateAction);
        expect(api.request).toBeCalled();
        expect(dispatch.mock.calls[1][0]).toEqual(rollbackHelpingStateAction);
    });
});
