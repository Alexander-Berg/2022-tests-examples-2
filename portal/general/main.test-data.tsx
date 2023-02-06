import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';

import empty from './mocks/empty.json';
import suggest from './mocks/suggest.json';

function draw(lsVal?: string): string {
    const req = mockReq({}, {
        JSON: {
            searchParams: {}
        },
        Services: {
            all_url: 'https://www-v32d7.wdevx.yandex.ru/all',
            hash: {
                '3': [
                    {
                        block: '1',
                        id: 'disk',
                        type: 3,
                        url: 'https://disk.yandex.ru/'
                    },
                    {
                        block: '1',
                        id: 'music',
                        type: 3,
                        url: 'https://music.yandex.ru/'
                    },
                    {
                        block: '1',
                        id: 'afisha',
                        type: 3,
                        url: 'https://afisha.yandex.ru/moscow?utm_source=yamain&utm_medium=yamain_afisha'
                    },
                    {
                        block: '1',
                        id: 'market',
                        type: 3,
                        url: 'https://market.yandex.ru/?clid=506'
                    }
                ]
            },
            processed: 1,
            show: 1
        },
        ClckBaseShort: 'yandex.ru/clck'
    });

    return '<style>.rows:before{visibility: hidden}</style><div class="rows">' +
        `<script>
            window.mocks = {
                empty: ${JSON.stringify(empty)},
                suggest: ${JSON.stringify(suggest)}
            };

            var oldAjax = $.ajax;
            $.ajax = function (opts) {
                if (opts.url.indexOf('suggest') > -1) {
                    if (opts.data.part === 'y') {
                        return $.Deferred().resolve(window.mocks.suggest);
                    } else {
                        return $.Deferred().resolve(window.mocks.empty);
                    }
                }
                return oldAjax.apply(this, arguments);
            };

            localStorage.setItem('mordaUserHistory', '${lsVal}');
        </script>` +
        execView('Main', {}, req) + '</div>';
}

export function arrow() {
    return draw();
}

export function arrowHistory() {
    return draw('{"history":["длина"],"isOn":true}');
}

export function arrowDisabledHistory() {
    return draw('{"history":[],"isOn":false}');
}
