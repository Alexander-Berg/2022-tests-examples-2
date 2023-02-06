import { execView } from '@lib/views/execView';
import { Body__deskNotif } from './body.view';

import noAuth from './mocks/noAuth.json';
import auth from './mocks/auth.json';
import router from './mocks/router.json';

export function notifNoAuth() {
    return `<script>
        var oldAjax = $.ajax;
        $.ajax = function (opts) {
            if (opts.url.indexOf('portal/api/data') > -1) {
                return $.Deferred().resolve(${JSON.stringify(noAuth)});
            }
            if (opts.url.indexOf('geohelper/api/v1/router') > -1) {
                return $.Deferred().resolve(${JSON.stringify(router)});
            }
            return oldAjax.apply(this, arguments);
        };
        // todo Выпилить
        home['export'] = home['export'] || {};
        home['export'].common = home['export'].common || {};
        home['export'].common.req = home['export'].common.req || {};
        </script>` + execView(Body__deskNotif);
}

export function notifAuth() {
    return `<script>
        var oldAjax = $.ajax;
        $.ajax = function (opts) {
            if (opts.url.indexOf('portal/api/data') > -1) {
                return $.Deferred().resolve(${JSON.stringify(auth)});
            }
            return oldAjax.apply(this, arguments);
        };
        // todo Выпилить
        home['export'] = home['export'] || {};
        home['export'].common = home['export'].common || {};
        home['export'].common.req = home['export'].common.req || {};
        </script>` + execView(Body__deskNotif);
}
