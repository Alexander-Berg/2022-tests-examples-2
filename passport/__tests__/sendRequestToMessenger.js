import api from '../../../../api';
jest.mock('../../../../api');

import sendRequestToMessenger from '../sendRequestToMessenger';
import {setAuthMessengerError, setAuthMessengerSent} from '../';
import {changePagePopupType, changePagePopupVisibility, domikIsLoading, setPasswordError} from '../../index';

jest.mock('../', () => ({
    setAuthMessengerError: jest.fn(),
    setAuthMessengerSent: jest.fn()
}));

jest.mock('../../', () => ({
    changePagePopupType: jest.fn(),
    changePagePopupVisibility: jest.fn(),
    domikIsLoading: jest.fn(),
    setPasswordError: jest.fn()
}));

describe('Actions: sendRequestToMessenger', () => {
    describe('success cases', () => {
        afterEach(() => {
            api.request.mockClear();
            changePagePopupVisibility.mockClear();
            changePagePopupType.mockClear();
            domikIsLoading.mockClear();
        });

        it('should send api request with valid params', () => {
            api.__mockSuccess({status: 'ok', code: ['1', '2']});

            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    track_id: 'track'
                },
                settings: {
                    language: 'ru'
                }
            }));

            sendRequestToMessenger()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/send_magic_letter', {
                csrf_token: 'csrf',
                language: 'ru',
                track_id: 'track',
                send_to: 'messenger'
            });
        });

        it('should dispatch appropriate actions after success response', () => {
            api.__mockSuccess({status: 'ok', code: ['1', '2']});
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    track_id: 'track'
                },
                settings: {
                    language: 'ru'
                }
            }));

            sendRequestToMessenger()(dispatch, getState);
            expect(setAuthMessengerSent).toBeCalledWith(['1', '2']);
            expect(changePagePopupVisibility).toBeCalledWith(true);
            expect(changePagePopupType).toBeCalledWith('authMessenger');
        });
    });

    describe('fail cases', () => {
        afterEach(() => {
            api.request.mockClear();
            changePagePopupVisibility.mockClear();
            changePagePopupType.mockClear();
            domikIsLoading.mockClear();
        });

        it('should handle errors', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    track_id: 'track'
                },
                settings: {
                    language: 'ru'
                }
            }));

            api.__mockFail({errors: ['magic_link.invalidated']});

            sendRequestToMessenger()(dispatch, getState);
            expect(setAuthMessengerError).toBeCalledWith('magic_link.invalidated');
        });

        it('should dispatch appropriate actions when error is "bot_api.request_failed"', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    track_id: 'track'
                },
                settings: {
                    language: 'ru'
                }
            }));

            api.__mockFail({errors: ['bot_api.request_failed']});

            sendRequestToMessenger()(dispatch, getState);
            expect(changePagePopupVisibility).toBeCalledWith(true);
            expect(changePagePopupType).toBeCalledWith('authMessengerInfo');
            expect(setPasswordError).toBeCalledWith('');
        });
    });
});
