import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { mockView } from '@lib/views/mock';
import { Ads } from '@lib/utils/ads';

/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-ignore
import { Headline } from '@block/headline/headline.view';
// @ts-ignore
import { DeskNotif } from '@block/desk-notif/desk-notif.view';
// @ts-ignore
import { Rows } from '@block/rows/rows.view';
// @ts-ignore
import { Row } from '@block/row/row.view';
// @ts-ignore
import { Container } from '@block/container/container.view';
// @ts-ignore
import { HomeArrow } from '@block/home-arrow/home-arrow.view';
// @ts-ignore
import { Xproc } from '@block/xproc/xproc.view';

import services from './mocks/services_tabs.json';

mockView(Headline, () => '');
mockView(DeskNotif, () => '');

mockView('win10-stripe', () => '');

function arrow(microphone: boolean, logo?: Req3Logo) {
    const settingsJs = home.settingsJs([]);
    const req = mockReq({}, {
        settingsJs,
        JSON: {
            common: {
                navigator: {},
                pageName: 'bender',
                language: 'ru'
            },
            search: {
                url: 'https://yandex.ru/search/',
                sample: {
                    id: '305058',
                    text: 'самый сильный супергерой',
                    serpArg: 'all',
                    counterPath: 'example.all',
                    nl: 1
                }
            }
        },
        Logo: logo,
        Services_tabs: services,
        BrowserDesc: {
            BrowserBase: 'Chromium',
            BrowserBaseVersion: '89.0.4389.82',
            BrowserEngine: 'WebKit',
            BrowserEngineVersion: '537.36',
            BrowserName: 'Chrome',
            BrowserVersion: '89.0.4389.82',
            CSP1Support: 1,
            CSP2Support: 1,
            OSFamily: 'Linux',
            SVGSupport: 1,
            SameSiteSupport: 1,
            WebPSupport: 1,
            historySupport: 1,
            isBrowser: 1,
            isMobile: 0,
            isTouch: 0,
            localStorageSupport: 1,
            postMessageSupport: 1,
            x64: 1
        },
        HostNameProd: 'yandex.ru',
        ClckBaseShort: 'yandex.ru/clck'
    });
    const resources = new home.Resources('white', req, execView);

    const content = execView(Xproc, {
        name: Container,
        mix: 'container__search container__line',
        content: {
            name: Row,
            mix: 'second',
            content: [
                { name: HomeArrow, data: {} }
            ]
        }
    }, req);

    return {
        htmlMix: ['i-ua_browser_desktop'],
        html: `<script>
            MBEM.blocks['mini-suggest'].prototype._request = function () {};
            BEM.blocks['i-voice'].hasMicSupport = function (cb) {
                setTimeout(function () {
                    cb(${microphone} ? null : {message: 'no api'});
                }, 0);
            };
            ${settingsJs.getRawScript(req)};
        </script>` + resources.getHTML('head') + content
    };
}

export function simple() {
    return arrow(true);
}

export function noMicro() {
    return arrow(false);
}

export function customLogo() {
    return arrow(false, {
        counter: '4nov2017',
        hoffset: '',
        voffset: '',
        href: '//ya.ru',
        show: 1,
        title: 'День народного единства',
        url: '4nov2017',
        width: '140',
        height: '100'
    });
}

const adbImage = 'https://yastatic.net/s3/home/garry_test_img/banner_test.png';

export function adbBanner() {
    let req: Req3Server = mockReq({}, {
        JSON: {
            common: {},
            search: {
                url: ''
            }
        },
        antiadb_desktop: 1,
        Banners: {
            banners: {
                banner: {
                    ad_nmb: '72057605002383905',
                    bnCounts: [],
                    click_url: '/empty',
                    height: 90,
                    hidpi_image: adbImage,
                    html5_iframe_src: '',
                    image: adbImage,
                    image_alt: 'Ехать, отправлять, встречать. Яндекс Go. 0+',
                    width: 728
                } as Req3BannerYabs
            }
        },
        HostNameProd: 'yandex.ru',
        ClckBaseShort: 'yandex.ru/clck'
    });
    req.ads = new Ads(req);
    req.resources = new home.Resources('white', req, execView);
    let res = execView(Rows, {}, req);
    return req.resources.getHTML('head') + '<script>' +
        'MBEM.blocks[\'mini-suggest\'].prototype._request = function () {};' +
        '</script>' + res;
}
