import {magicDoneCallback} from '../magicDoneCallback';
import {magicService} from '@blocks/AuthSilent/magicService';

jest.mock('@blocks/AuthSilent/magicService', () => ({
    magicService: {
        stop: jest.fn(),
        trackId: 'qwer'
    }
}));
jest.mock('@blocks/metrics', () => ({
    goal: jest.fn()
}));

const {location} = window;

describe('authv2/magic/magicDonecallback', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });
    it('should change location on state auth_challenge', () => {
        delete window.location;
        window.location = {
            href: 'some url'
        };

        magicDoneCallback({state: 'auth_challenge', redirectUrl: 'redirect/test'});
        expect(magicService.stop).toBeCalled();
        expect(window.location.href).toEqual('redirect/test');
        window.location = location;
    });
    it('should redirect to /auth/finish on state otp_auth_finished', () => {
        delete window.location;
        window.location = {
            href: 'some url'
        };

        magicDoneCallback({status: 'ok', state: 'otp_auth_finished'});
        expect(magicService.stop).toBeCalled();
        expect(window.location.href).toEqual('/auth/finish/?track_id=qwer');
        window.location = location;
    });
});
