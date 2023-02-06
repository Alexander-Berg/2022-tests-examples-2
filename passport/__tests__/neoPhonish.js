import api from '@blocks/api';
import {changePagePopupType, changePagePopupVisibility, domikIsLoading} from '@blocks/authv2/actions';
import {updateErrors} from '@blocks/actions/form';
import {
    setPhoneConfirmationDenyResendUntilTime,
    updatePhoneNumber,
    setPhoneConfirmationInternationalPhoneNumber
} from '@blocks/actions/phoneConfirm';
import sendToChallenge from '@blocks/authv2/actions/challenge/sendToChallenge';
import metrics from '@blocks/metrics';
import {amSetAnalyticsToRetpath} from '@blocks/authv2/actions/nativeMobileApi';
// eslint-disable-next-line no-duplicate-imports
import {neoPhonishAuth} from '../neoPhonish';

jest.mock('@blocks/api', () => ({
    neoPhonishAuth: jest.fn(),
    amSetAnalyticsToRetpath: jest.fn()
}));
jest.mock('@blocks/authv2/actions', () => ({
    domikIsLoading: jest.fn(),
    changePagePopupType: jest.fn(),
    changePagePopupVisibility: jest.fn()
}));
jest.mock('@blocks/actions/form', () => ({
    updateErrors: jest.fn()
}));
jest.mock('@blocks/actions/phoneConfirm', () => ({
    setPhoneConfirmationDenyResendUntilTime: jest.fn(),
    updatePhoneNumber: jest.fn(),
    setPhoneConfirmationInternationalPhoneNumber: jest.fn()
}));
jest.mock('@blocks/metrics', () => ({
    goal: jest.fn(),
    send: jest.fn()
}));
jest.mock('@blocks/authv2/actions/challenge/sendToChallenge', () => ({
    default: jest.fn()
}));
jest.mock('@blocks/authv2/actions/nativeMobileApi', () => ({
    amRequestSmsCode: jest.fn(),
    amSetAnalyticsToRetpath: jest.fn()
}));

const mockLocationSetter = jest.fn();

const originalLocation = window.location;

describe('Actions: neoPhonish', () => {
    beforeEach(() => {
        api.neoPhonishAuth.mockImplementation(() => {
            return {
                then(callback = () => {}) {
                    callback({status: 'ok'});

                    return {
                        catch() {}
                    };
                }
            };
        });

        Object.defineProperty(window, 'location', {
            set: mockLocationSetter
        });
    });

    afterEach(() => {
        api.neoPhonishAuth.mockClear();
        domikIsLoading.mockClear();
        changePagePopupType.mockClear();
        changePagePopupVisibility.mockClear();
        updateErrors.mockClear();
        setPhoneConfirmationDenyResendUntilTime.mockClear();
        updatePhoneNumber.mockClear();
        setPhoneConfirmationInternationalPhoneNumber.mockClear();
        metrics.goal.mockClear();
        metrics.send.mockClear();
        sendToChallenge.default.mockClear();
        amSetAnalyticsToRetpath.mockClear();
        mockLocationSetter.mockClear();
        Object.defineProperty(window, 'location', originalLocation);
    });

    it('should navigate to profile after auth', () => {
        const getState = jest.fn(() => ({
            common: {
                askEmailUrl: 'askEmailUrl',
                askPhoneUrl: 'askPhoneUrl',
                profile_url: '/profile'
            },
            am: {
                isAm: false,
                finishOkUrl: '/amFinishOk'
            }
        }));

        const dispatch = jest.fn((action) => {
            if (typeof action === 'function') {
                return action(dispatch, getState);
            }
        });

        neoPhonishAuth({})(dispatch, getState);

        expect(mockLocationSetter).toBeCalledWith('/profile');
    });

    it('should navigate to retpath after auth', () => {
        const getState = jest.fn(() => ({
            common: {
                askEmailUrl: 'askEmailUrl',
                askPhoneUrl: 'askPhoneUrl',
                profile_url: '/profile',
                retpath: '/retpath'
            },
            am: {
                isAm: false,
                finishOkUrl: '/amFinishOk'
            }
        }));

        const dispatch = jest.fn((action) => {
            if (typeof action === 'function') {
                return action(dispatch, getState);
            }
        });

        neoPhonishAuth({})(dispatch, getState);

        expect(mockLocationSetter).toBeCalledWith('/retpath');
    });

    it('should navigate to retpath after auth, even though amFinishOk specified', (done) => {
        const getState = jest.fn(() => ({
            common: {
                askEmailUrl: 'askEmailUrl',
                askPhoneUrl: 'askPhoneUrl',
                profile_url: '/profile',
                retpath: '/retpath'
            },
            am: {
                isAm: true,
                finishOkUrl: '/amFinishOk'
            }
        }));

        const dispatch = jest.fn((action) => {
            if (typeof action === 'function') {
                return action(dispatch, getState);
            }
        });

        neoPhonishAuth({})(dispatch, getState);

        setTimeout(() => {
            expect(mockLocationSetter).toBeCalledWith('/retpath');
            expect(amSetAnalyticsToRetpath).toBeCalledTimes(1);

            done();
        });
    });
});
