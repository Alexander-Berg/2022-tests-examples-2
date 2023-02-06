import api from '../../../api';
import checkAuthLetterStatus from '../checkAuthLetterStatus';

import {
    domikIsLoading,
    setAuthMailError,
    setAuthMailCancelled,
    changePagePopupVisibility,
    changePagePopupType
} from '../';

jest.mock('../../../api');
jest.mock('../', () => ({
    domikIsLoading: jest.fn(),
    setAuthMailError: jest.fn(),
    magic_link_confirmed: jest.fn(),
    setAuthMailCancelled: jest.fn(),
    changePagePopupVisibility: jest.fn(),
    changePagePopupType: jest.fn()
}));

const {location} = window;
const dispatch = jest.fn();
const getState = jest.fn(() => ({
    common: {
        csrf: 'csrf',
        track_id: 'track'
    },
    mailAuth: {
        isEnabled: true
    },
    auth: {
        processedAccount: {
            uid: 'account.uid',
            primaryAliasType: 5
        }
    }
}));

describe('Action checkAuthLetterStatus', () => {
    describe('success cases', () => {
        beforeEach(() => {
            delete window.location;
            window.location = {
                href: '/auth/finish/?track_id=track'
            };
        });

        afterEach(() => {
            window.location = location;
            api.request.mockClear();
            domikIsLoading.mockClear();
        });

        it('should send api request with valid params', () => {
            checkAuthLetterStatus()(dispatch, getState);

            expect(api.request).toBeCalledWith('/auth/letter/status/', {
                csrf_token: 'csrf',
                track_id: 'track'
            });
        });

        it('it should call window.location href if response is ok and magic_link_confirmed is true', () => {
            api.__mockSuccess({status: 'ok', magic_link_confirmed: true, track_id: 'track_id'});

            checkAuthLetterStatus()(dispatch, getState);
            expect(window.location.href).toEqual('/auth/finish/?track_id=track_id');
        });

        it('should dispatch setAuthMailCancelled if response is ok, but magic_link_confirmed is false', () => {
            api.__mockSuccess({status: 'ok', magic_link_confirmed: false});

            checkAuthLetterStatus()(dispatch, getState);
            expect(setAuthMailCancelled).toBeCalledWith(false);
        });

        it('should dispatch changePagePopupVisibility if response is ok, but magic_link_confirmed is false', () => {
            api.__mockSuccess({status: 'ok', magic_link_confirmed: false});

            checkAuthLetterStatus()(dispatch, getState);
            expect(changePagePopupVisibility).toBeCalledWith(true);
        });

        it('should dispatch changePagePopupType if response is ok, but magic_link_confirmed is false', () => {
            api.__mockSuccess({status: 'ok', magic_link_confirmed: false});

            checkAuthLetterStatus()(dispatch, getState);
            expect(changePagePopupType).toBeCalledWith('authLetter');
        });
    });
    describe('fail cases', () => {
        beforeEach(() => {
            api.__mockFail({errors: ['magic_link.invalidated']});
        });

        afterEach(() => {
            api.request.mockClear();
            setAuthMailError.mockClear();
        });

        it('should handle failed request', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                },
                mailAuth: {
                    track_id: 'track'
                },
                auth: {
                    processedAccount: {
                        uid: 'account.uid',
                        primaryAliasType: 5
                    }
                }
            }));

            checkAuthLetterStatus()(dispatch, getState);
            expect(setAuthMailError).toBeCalledWith('magic_link.invalidated');
        });
    });
    describe('always', () => {
        beforeEach(() => {
            api.__mockAlways();
        });

        afterEach(() => {
            api.request.mockClear();
            domikIsLoading.mockClear();
        });

        it('should call action for loader with false value', () => {
            checkAuthLetterStatus()(dispatch, getState);
            expect(domikIsLoading).toBeCalledWith(false);
        });
    });
});
