import {checkGeoLocation} from '../check_geolocation';
import {setGeoLocationStatus} from '../';

jest.mock('../', () => ({
    setGeoLocationStatus: jest.fn()
}));

describe('Action: checkGeoLocation', () => {
    it('should dispatch setGeoLocationStatus', () => {
        const dispatch = jest.fn();

        window.navigator.geolocation = jest.fn();

        checkGeoLocation()(dispatch);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);
        expect(setGeoLocationStatus).toBeCalled();
        expect(setGeoLocationStatus).toBeCalledWith(true);
    });

    it('should dispatch setGeoLocationStatus', () => {
        const dispatch = jest.fn();

        window.navigator.geolocation = false;

        checkGeoLocation()(dispatch);

        expect(dispatch.mock.calls.length).toBe(0);
    });
});
