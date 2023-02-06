import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { GeolocationSetup } from './geolocation-setup.view';

export const simple =  () => {
    return `<script>
        window.home = window.home || {};
        home['export'] = {'geolocation-setup': {guide:{
            content: 'Узнать, как включить',
            href: '//ya.ru'
        }}};
    </script>` +
    execView(GeolocationSetup, {}, mockReq({}, {
        MordaZone: 'ru',
    }));
};
