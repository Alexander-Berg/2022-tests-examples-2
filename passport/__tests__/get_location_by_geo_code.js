import api from '../../../../api';

jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import {getLocationByGeoCode} from '../get_location_by_geo_code';

describe('Action: getLocationByGeoCode', () => {
    it('should call geocode.addresses api', () => {
        const geoCode = 'geocode';
        const lang = 'en_GB';
        const detail = true;
        const csrf = 'token';

        getLocationByGeoCode(geoCode, lang, detail, csrf);

        expect(api.request).toBeCalled();
        expect(api.request).toBeCalledWith('geocode.addresses', {geoCode, lang, detail, csrf}, {abortPrevious: true});
    });

    it('should call geocode.addresses api with default language', () => {
        const geoCode = 'geocode';
        const detail = true;
        const csrf = 'token';

        getLocationByGeoCode(geoCode, undefined, detail, csrf);

        expect(api.request).toBeCalled();
        expect(api.request).toBeCalledWith(
            'geocode.addresses',
            {geoCode, lang: 'ru_RU', detail, csrf},
            {abortPrevious: true}
        );
    });
});
