import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { GeolocationPromo } from './geolocation-promo.view';

export const simple = () => {
    return `<script>
        if ('permissions' in navigator) {
            navigator.permissions.query = function () {
                return Promise.resolve({state: 'prompt'});
            };
        }
    </script>` +
    execView(GeolocationPromo, {}, mockReq({}, {
        isAndroid: 1,
        GeoDetection: {},
        options: {},
        JSON: {},
        geolocation_promo: 1,
        cookie_set_gif: '/empty?'
    }));
};
