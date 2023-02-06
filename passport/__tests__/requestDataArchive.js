import api from '../../../api';
import {updateTakeoutStatus, handleInternalError, updateLoadingStatus, updateTakeoutData} from '../';
import requestDataArchive from '../requestDataArchive';

jest.mock('../../../api');
jest.mock('../', () => ({
    updateLoadingStatus: jest.fn(),
    handleInternalError: jest.fn(),
    updateTakeoutStatus: jest.fn(),
    updateTakeoutData: jest.fn()
}));

const dispatch = jest.fn();
const getState = jest.fn(() => ({
    common: {
        csrf: 'csrf',
        uid: '23452'
    }
}));

describe('requestDataArchive', () => {
    it('should dispatch updateLoadingStatus', () => {
        requestDataArchive()(dispatch, getState);

        expect(updateLoadingStatus).toBeCalled();
    });

    describe('requestDataArchive request succeeded', () => {
        beforeEach(() => {
            api.__mockSuccess({status: 'ok'});
        });

        afterEach(() => {
            api.request.mockClear();
        });

        it('should call api with profile/request-data-archive url', () => {
            requestDataArchive()(dispatch, getState);

            expect(api.request).toBeCalledWith('profile/request-data-archive', {csrf_token: 'csrf', uid: '23452'});
        });

        it('should dispatch updateTakeoutStatus', () => {
            requestDataArchive()(dispatch, getState);

            expect(updateTakeoutStatus).toBeCalledWith('isBeingRequesting');
        });

        it('should dispatch updateTakeoutData with error: ""', () => {
            requestDataArchive()(dispatch, getState);

            expect(updateTakeoutData).toBeCalledWith({
                field: 'error',
                value: ''
            });
        });
    });

    describe('requestDataArchive request failed', () => {
        afterEach(() => {
            api.request.mockClear();
            handleInternalError.mockClear();
            updateTakeoutStatus.mockClear();
        });

        it('should call updateTakeoutStatus if error is "action.not_required"', () => {
            api.__mockFail({status: 'error', errors: ['action.not_required']});
            requestDataArchive()(dispatch, getState);

            expect(updateTakeoutStatus).toBeCalledWith('isBeingRequesting');
            expect(handleInternalError).not.toBeCalled();
        });

        it('should call handleInternalError', () => {
            api.__mockFail({status: 'error', errors: ['account.disabled']});
            requestDataArchive()(dispatch, getState);

            expect(handleInternalError).toBeCalled();
            expect(updateTakeoutStatus).not.toBeCalled();
        });
    });
});
