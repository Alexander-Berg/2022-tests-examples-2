import api from '../../../api';
import {updateLoadingStatus, updateTakeoutData, setLinkLoadingStatus, handleInternalError} from '../';
import getArchiveData from '../getArchiveData';
import handleArchiveLink from '../../components/DataInfoContent/handleArchiveLink';

jest.mock('../../../api');
jest.mock('../', () => ({
    updateLoadingStatus: jest.fn(),
    updateTakeoutData: jest.fn(),
    setLinkLoadingStatus: jest.fn(),
    handleInternalError: jest.fn()
}));
jest.mock('../../components/DataInfoContent/handleArchiveLink');

const dispatch = jest.fn();
const getState = jest.fn(() => ({
    common: {
        csrf: 'csrf',
        uid: '23452'
    }
}));

describe('getArchiveData', () => {
    it('should dispatch updateLoadingStatus', () => {
        getArchiveData()(dispatch, getState);
        expect(updateLoadingStatus).toBeCalled();
        expect(setLinkLoadingStatus).toBeCalled();
    });

    describe('getArchiveData, request succeeded', () => {
        beforeEach(() => {
            api.__mockSuccess({status: 'ok', archiveUrl: '//s3.getdata.zip'});
        });

        afterEach(() => {
            api.request.mockClear();
            updateTakeoutData.mockClear();
        });

        it('should dispatch updateTakeoutData', () => {
            getArchiveData()(dispatch, getState);
            expect(updateTakeoutData).toBeCalledWith({
                field: 'archiveUrl',
                value: '//s3.getdata.zip'
            });
        });

        it('should call handleArchiveLink', () => {
            getArchiveData()(dispatch, getState);
            expect(handleArchiveLink).toBeCalled();
        });
    });

    describe('getArchiveData, request failed', () => {
        beforeEach(() => {
            api.__mockFail({errors: ['account.not_found']});
        });

        afterEach(() => {
            api.request.mockClear();
            updateTakeoutData.mockClear();
        });

        it('should dispatch handleInternalError', () => {
            getArchiveData()(dispatch, getState);
            expect(handleInternalError).toBeCalled();
        });

        it('should handle "action.impossible" error', () => {
            api.__mockFail({errors: ['action.impossible']});

            getArchiveData()(dispatch, getState);
            expect(updateTakeoutData).toBeCalledWith({
                field: 'error',
                value: 'TakeOut.getdata_url-error'
            });
        });
    });
});
