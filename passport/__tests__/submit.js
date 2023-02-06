import api from '../../../../api';
jest.mock('../../../../api');

import {updateTrack} from '../../../../common/actions';
import {domikIsLoading} from '../../';
import {clearErrors, setErrors} from '../';

jest.mock('../../../../common/actions', () => ({
    updateTrack: jest.fn()
}));
jest.mock('../../', () => ({
    domikIsLoading: jest.fn()
}));
jest.mock('../', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn()
}));

import submit from '../submit';

describe('Actions: confirmPhone', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            clearErrors.mockClear();
            setErrors.mockClear();
            updateTrack.mockClear();
            domikIsLoading.mockClear();
        });

        it('should send request', () => {
            const dispatch = jest.fn();
            const trackId = 'trackId';

            api.__mockSuccess({status: 'ok', track_id: trackId});

            submit()(dispatch);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(api.request).toBeCalledWith('auth/restore_login/submit');
            expect(domikIsLoading).toBeCalledWith(true);
            expect(clearErrors).toBeCalled();
            expect(updateTrack).toBeCalledWith(trackId);
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            clearErrors.mockClear();
            setErrors.mockClear();
            updateTrack.mockClear();
            domikIsLoading.mockClear();
        });

        it('should send request', () => {
            const dispatch = jest.fn();

            api.__mockFail({status: 'ok'});

            submit()(dispatch);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(api.request).toBeCalledWith('auth/restore_login/submit');
            expect(domikIsLoading).toBeCalledWith(true);
            expect(clearErrors).toBeCalled();
            expect(setErrors).toBeCalledWith(['internal']);
        });
    });

    describe('always cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            clearErrors.mockClear();
            setErrors.mockClear();
            updateTrack.mockClear();
            domikIsLoading.mockClear();
        });

        it('should send request', () => {
            const dispatch = jest.fn();

            api.__mockAlways({status: 'ok'});

            submit()(dispatch);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(api.request).toBeCalledWith('auth/restore_login/submit');
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0]).toEqual([true]);
            expect(domikIsLoading.mock.calls[1]).toEqual([false]);
            expect(clearErrors).toBeCalled();
        });
    });
});
