const thisMockBase = '?datafile=touch/blocks/touch/banner/banner.test-data.js',
    imgBase = require('../../../../frontend-node/lib/dummyimage').patternRedBorder,
    yabsImg = `${imgBase}&for=yabs&w=320&h=67&color=rgb(200,160,66)`,
    rtbImage = `${imgBase}&for=rtbImage&w=640&h=134&color=rgb(128,128,128)`;

const noBanner = {
        Banners: {}
    },
    yabsBanner = {
        Banners: {
            pixelBase: `${thisMockBase}&dataname=pixelbase`,
            banners: {
                banner: {
                    bannerid: '123',
                    bnHref: `${thisMockBase}&dataname=counter#yabshref`,
                    bnAlt: 'yabs',
                    bnImg: yabsImg,
                    bnH: 67,
                    bnW: 320,
                    gif_tizer: '',
                    product: 'lavka-app',
                    textauthor: '',
                    linknext: '&dataname=linknext',
                    bnCount: `${thisMockBase}&dataname=counter&counts`
                }
            }
        }
    },
    direct = {
        data: {
            common: {
                linkHead: `${thisMockBase}&dataname=counter`
            },
            settings: {
                '1': {
                }
            },
            direct: {
                directTitle: {
                    title: 'Direct Title',
                    url: '#direct-url'
                },
                ads: [
                    {
                        linkTail: '&direct-link-tail',
                        url: `${thisMockBase}&dataname=counter#directclick`,
                        title: 'Заголовок масимально длинный чтобы проверить все заполняемое пространство которое ему предоставлено',
                        body: 'Текст рекламы, который рекламирует рекламу и вмещается в блок',
                        abuseUrl: `${thisMockBase}&dataname=counter&abuse`,
                        domain: 'b-lesb-lesb-lesb-lesb-les.com',
                        images: [
                            [`${imgBase}&for=direct&w=160&h=167&color=rgb(112,67,240)`, 160, 167]
                        ]
                    }
                ]
            }
        }
    },
    directFirstlook = {
        Direct_ad_firstlook: direct
    },
    directBackfill = {
        Direct_ad: direct
    },
    refresh = {
        BannersRefresh: {
            refresh_counts: 5,
            tab_timeout: 15,
            watch_timeout: 2,
            refresh_url: `${thisMockBase}&dataname=refreshMock`
        }
    },
    broAndroid = {
        BrowserDesc: {
            BrowserName: 'ChromeMobile',
            BrowserVersion: '71.0.3578',
            OSFamily: 'Android',
            OSVersion: '8.0',
            isTablet: 0
        }
    },
    broAndroidTablet = {
        BrowserDesc: Object.assign({}, broAndroid.BrowserDesc, {
            isTablet: 1
        })
    },
    rtbMetaExp = {
        meta_rtb: {
            exp: {
                content: 'all',
                domain: 'kubru',
                exp_slot: '0',
                from: '2019-03-26',
                geos: '10000',
                id: 'meta_rtb',
                info: 'новая ручка рекламы. десктоп',
                new_yuid: '1',
                percent: '100',
                selector: 'yandexuid_salted',
                yandex: '1',
                yandex_669: '1'
            },
            flags: {
                id: 'meta_rtb',
                newyandexuid: 1,
                on: 1,
                use_stat_prefix: 1,
                yandex: 1,
                yandex_669: 1,
                yandexuid: 1
            },
            id: 'meta_rtb',
            on: 1
        }
    },
    rtbMetaSettings = {
        linkTail: `${thisMockBase}&dataname=RtbCounter`,
        viewNotices: [`${thisMockBase}&dataname=counter&view`],
        bannerIds: [
            6561502500
        ]
    },
    metaRtbDirect = {
        exp: rtbMetaExp,
        RTBMeta: {
            data: {
                common: direct.data.common,
                direct: direct.data.direct,
                settings: rtbMetaSettings
            },
            processed: 1,
            show: 1
        }
    },
    metaRtbImage = {
        exp: rtbMetaExp,
        RTBMeta: {
            data: {
                rtb: {
                    url: `${thisMockBase}#rtbclick`,
                    basePath: 'https://storage.mds.yandex.net/get-canvas-html5/1003119/bf1f886a-e526-4c09-941f-80679eac8854/',
                    height: 134,
                    width: 640,
                    clickUrl: `${thisMockBase}#rtbclick`,
                    posterSrc: rtbImage,
                    abuseLink: '//an.yandex.ru/abuse'
                },
                visibilitySettings: {
                    delay: 2000
                },
                settings: rtbMetaSettings
            },
            processed: 1,
            show: 1
        }
    },
    metaRtbImageSocial = {
        RTBMeta: {
            data: {
                rtb: {
                    url: `${thisMockBase}#rtbclick`,
                    basePath: 'https://storage.mds.yandex.net/get-canvas-html5/1003119/bf1f886a-e526-4c09-941f-80679eac8854/',
                    height: 134,
                    width: 640,
                    clickUrl: `${thisMockBase}#rtbclick`,
                    posterSrc: rtbImage,
                    abuseLink: '//an.yandex.ru/abuse/'
                },
                visibilitySettings: {
                    delay: 2000
                },
                settings: {
                    ...rtbMetaSettings,
                    bannerFlags: 'animated,social_advertising'
                }
            },
            processed: 1,
            show: 1
        }
    };

function getDraw(...data) {
    return (execView, {home, js, css, documentMods, pageModeList}) => {
        let resources = {};

        const req = data.reduce(home.deepExtend, {
            ua: {},
            UserDevice: {
                ratio: '2'
            },
            MordaZone: 'ru',
            settingsJs: home.settingsJs({}),
            options: {},
            Banners_pages: '123'
        });

        req.resources = new home.Resources('touch', req, execView);

        req.resources.addBundle = () => '';
        req.resources.add = function(block, blockName) {
            resources[blockName] = resources[blockName] || [];
            resources[blockName].push(block);
        };

        let banner = execView('Banner', req);
        let bannerStyle = (resources['inline-css'] || []).join('');

        return `<!DOCTYPE html>
            <html class="${documentMods}">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width">
                <link rel="stylesheet" type="text/css" href="${css}">
                <style>
                    body {
                        overflow: hidden;
                    }
                    .scroller {
                        overflow: hidden;
                    }
                    *, *:before, *:after {
                        transition-duration: 0s !important;
                        transition-delay: 0s !important;
                        animation-duration: 0s !important;
                        animation-delay: 0s !important;
                    }
                    .direct-touch {
                        margin: 0 !important;
                    }
                    .banner__frame-wrap {
                        margin: 0 !important;
                    }
                </style>
                <script src="/tmpl/common/detector.inline.js"></script>
                <script src="/tmpl/common/blocks/home/__load-manager/home__load-manager-inline.js"></script>
                <script src="https://yastatic.net/jquery/2.1.4/jquery.min.js"></script>
                <script src="/node_modules/sinon/pkg/sinon.js"></script>
                ${execView('IUa2__script', req)}
                <style>
                    .test-container {
                        margin-top: 5px;
                        border-bottom: 1px dashed lime;
                    }
                    ${bannerStyle}
                </style>
            </head>
            <body class="${pageModeList}">
                <div class="test-container">
                    ${banner}
                </div>
                <script>${req.settingsJs.getRawScript(req)}</script>
                <script src="${js}"></script>
                <script>
                    window.logPathSpy = sinon.spy(home.stat, 'logPath');
                    (function() {
                        if (window.$ && window.$.fn) {
                            $.fx.off = true;

                            $('.i-delayed-bem').addClass('i-bem');
                            $('.i-bundle-bem').addClass('i-bem');

                            if (window.BEM) {
                                BEM.DOM.init();
                            }
                        }
                    })();
                </script>
                <div style="display: none" id="loaded-mark"></div>
            </body>
        </html>`;
    };
}

module.exports = {
    noBanner: getDraw(broAndroid, noBanner),
    yabsPhone: getDraw(broAndroid, yabsBanner),
    yabsTablet: getDraw(broAndroidTablet, yabsBanner),
    yabsStatpixelPhone: getDraw(broAndroid, yabsBanner),
    yabsStatpixelTablet: getDraw(broAndroidTablet, yabsBanner),
    directPhone: getDraw(broAndroid, directFirstlook, yabsBanner),
    directTablet: getDraw(broAndroidTablet, directFirstlook, yabsBanner),
    directBackfillPhone: getDraw(broAndroid, directBackfill, yabsBanner),
    directBackfillTablet: getDraw(broAndroidTablet, directBackfill, yabsBanner),
    directPhoneRefresh: getDraw(broAndroid, directFirstlook, refresh),

    metaRtbDirect: getDraw(broAndroid, metaRtbDirect),
    metaRtbImage: getDraw(broAndroid, metaRtbImage),
    metaRtbImageSocial: getDraw(broAndroid, metaRtbImageSocial),
    counter: () => {
        return '<body><script>document.write("this is " + location.hash);document.close()</script><body>';
    },
    refreshMock: (execView, {query}) => {
        return `<style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
            }
            body:before {
                content: '';
                display: block;
                padding-top: 20.9375%;
            }
            .box {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                border: 3px solid #f80;
                box-sizing: border-box;
            </style>
            <body>
                <script>
                    window.parent.postMessage('{"name": "yabs","bannerId": "test"}', '*');
                    setTimeout(function() {
                          window.parent.postMessage({"showedCounter": "readyForRefresh"}, '*');
                    }, 2000)
                </script>
                <div class="box">
                    this is refresh ${query['skip-token'] || ''}
                </div>
            </body>`;
    }
};
