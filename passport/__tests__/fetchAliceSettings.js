jest.mock('@blocks/api', () => ({request: jest.fn()}));

import {setLoadingAlice, setAliceSettings, setAliceDevices} from '../actions/actions';
import {fetchSettings} from '../api';
import * as api from '@blocks/api';

describe('thunk fetchAliceSettings', () => {
    const doneResult = {ok: true};
    const csrf = 'csrf';
    const track_id = 'track_id';
    const uid = 'uid';
    const getState = jest.fn(() => ({
        common: {
            csrf,
            uid,
            track_id
        }
    }));
    const dispatch = jest.fn();

    const mockApi = ({success = true} = {}) => {
        api.request.mockImplementation(() => {
            const FakeApi = function() {
                this.done = function(fn) {
                    if (success) {
                        const result = Object.assign({}, doneResult);

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

    it('Loading is setted and removed', async () => {
        const promise = fetchSettings(true)(dispatch, getState);

        expect(dispatch.mock.calls[0][0]).toEqual(setLoadingAlice(true));
        expect(dispatch).not.toBeCalledWith(setLoadingAlice(false));
        await promise;
        expect(dispatch).toBeCalledWith(setLoadingAlice(false));
    });

    it('Do dispatch setAliceSettings and setAliceDevices if responce is good', async () => {
        await fetchSettings(true)(dispatch, getState);

        expect(api.request).toBeCalled();
        expect(dispatch).toBeCalledWith(setAliceSettings(Object.assign({}, doneResult)));
        expect(dispatch).toBeCalledWith(setAliceDevices(Object.assign({}, doneResult)));
    });

    it("Don't dispatch setAliceSettings and setAliceDevices if responce is bad", async () => {
        mockApi({success: false});
        await fetchSettings(true)(dispatch, getState);

        expect(api.request).toBeCalled();
        expect(dispatch).not.toBeCalledWith(setAliceSettings(Object.assign({}, doneResult)));
        expect(dispatch).not.toBeCalledWith(setAliceDevices(Object.assign({}, doneResult)));
    });
});
