import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Promo, Position, SearchSelectNativePromo } from '@block/search-select-native-promo/search-select-native-promo.view';
import { capitalize } from '@lib/text/capitalize';

const baseHtml = (
    <>
        <style>{
            `body {
                background: #fff;
            }
            .document_dark_yes body {
                background: #000;
            }`
        }
        </style>
        <div class="body__wrapper">
            <div class="i_bem"><div class="dialog__overlay" /></div>
            <div class="dialog__wrapper">
                <div class="dialog__list" />
            </div>
        </div>
        <div class="area" />
    </>
);

const reqFromType = (type: Promo, size?: Position, theme?: 'overlay') => mockReq({}, {
    BrowserDesc: {
        BrowserName: 'Safari',
        isTouch: 1,
        isMobile: 1,
        isBrowser: 1,
        BrowserEngine: '',
        OSFamily: 'iOS'
    },
    iOSVersion: '13',
    Popup_system: {
        distribution: {
            systembanner: [
                {
                    code: {
                        image: 'https://avatars.mds.yandex.net/get-direct-picture/45743/gRL4dkBfyVL38sMg0rfiPQ/orig',
                        title: 'Настройка поиска в Safari',
                        snippet: 'Сделать Яндекс основным поиском?',
                        link: '#',
                        button_no: 'Не надо',
                        button_yes: 'Да',
                        styles: {
                            // system, system-center, e.t.c
                            type,
                            size
                        },
                        close_counter: '?search-select-native-promo_close=1',
                        theme
                    }
                }
            ]
        }
    }
});

const toExport: {[key: string]: unknown} = {};

const prepareExport = (promoType: string, mod: string, position: Position, theme?: 'overlay') => {
    const reqMod = mod.length > 0 ? `-${mod}` : mod;
    const req = reqFromType(`${promoType}${reqMod}`, position, theme);

    const promoName = `${promoType}${capitalize(mod)}${capitalize(position)}${capitalize(theme || '')}`;

    toExport[promoName] = () => {
        return baseHtml + execView(SearchSelectNativePromo, {}, req);
    };

    toExport[`${promoName}Night`] = () => {
        return {
            html: baseHtml + execView(SearchSelectNativePromo, {}, Object.assign({ Skin: 'night' }, req)),
            skin: 'night'
        };
    };
};

for (const promoType of ['ios', 'system']) {
    for (const mod of ['', 'icon']) {
        for (const position of ['left', 'right'] as Position[]) {
            prepareExport(promoType, mod, position);
        }
    }
    for (const mod of ['center', 'icon-center']) {
        for (const position of ['above', 'below'] as Position[]) {
            prepareExport(promoType, mod, position);
        }
    }
}

for (const mod of ['', 'blue']) {
    for (const position of ['down', 'center'] as Position[]) {
        for (const theme of [undefined, 'overlay' as const]) {
            prepareExport('chrome', mod, position, theme);
        }
    }
}
prepareExport('system', '', 'one');

const reqSystemCenter = reqFromType('system-center');

toExport.center = function() {
    return baseHtml + execView(SearchSelectNativePromo, {}, reqSystemCenter);
};

toExport.centerCookie = function() {
    return baseHtml + execView(SearchSelectNativePromo, {}, Object.assign(
        {}, reqSystemCenter, {
            cookie_set_gif: '?cookie_test_url',
            ab_flags: {
                yp_show_system_center: {
                    value: '1'
                }
            }
        },
    ));
};

module.exports = toExport;
