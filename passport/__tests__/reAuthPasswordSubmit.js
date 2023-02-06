jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import reAuthPasswordSubmit from '../reAuthPasswordSubmit';
import {updateMagicTokensSuccess} from '../';
import * as api from '../../../api';

jest.mock('../', () => ({
    updateMagicTokensSuccess: jest.fn()
}));

describe('Actions: reAuthPasswordSubmit', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({track_id: 'track', csrf_token: 'new_token'});
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            updateMagicTokensSuccess.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    retpath: 'retpath'
                }
            }));

            reAuthPasswordSubmit()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith(
                'reAuthPasswordSubmit',
                expect.objectContaining({
                    csrf_token: 'csrf',
                    retpath: 'retpath'
                })
            );
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(1);
            expect(updateMagicTokensSuccess).toBeCalled();
            expect(updateMagicTokensSuccess).toBeCalledWith('track', 'new_token');
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                }
            }));

            reAuthPasswordSubmit()(dispatch, getState);

            expect(api.request).toBeCalled();

            expect(api.request).not.toBeCalledWith(
                'reAuthPasswordSubmit',
                expect.objectContaining({
                    retpath: expect.anything()
                })
            );

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(1);
            expect(updateMagicTokensSuccess).toBeCalled();
            expect(updateMagicTokensSuccess).toBeCalledWith('track', 'new_token');
        });
    });
});
