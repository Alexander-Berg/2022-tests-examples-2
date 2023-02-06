/* eslint-disable @typescript-eslint/no-explicit-any */
import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { BBanner } from '@block/b-banner/b-banner.view';
import { Ads } from '@lib/utils/ads';

describe('b-banner', function() {
    const mockAbstractDirectData: Partial<Req3Server> = {
        common: {
            linkHead: 'https://an.yandex.ru/head'
        },
        direct: {
            ads: [
                {
                    adId: 6529330059,
                    title: 'Заголовок',
                    body: 'Только 3 дня! VW MULTIVAN Style всего от 3 609 700 ₽ в Нева-Автоком. Звоните сейчас!',
                    url: 'https://an.yandex.ru/link_1',
                    linkTail: '+tail_1',
                    domain: 'ya.ru',
                    images: [
                        [
                            '//avatars.mds.yandex.net/get-direct/238679/BLFf8_rcQqoJZ5-0jef8Lg/wx1080',
                            '1080',
                            '607'
                        ]
                    ],
                    abuseUrl: 'https://an.yandex.ru/abuse_1',
                    addInfo: {
                        type: 'callouts',
                        callouts_list: [
                            'Спутниковая связь',
                            'Прокат снаряжения',
                            'Сертификат',
                            'С нами безопасно'
                        ]
                    }
                }
            ],
            directTitle: {
                title: 'Яндекс.Директ',
                url: 'https://direct.yandex.ru/?partner'
            }
        }
    };
    const tgoSettings: Partial<Req3Server> = {
        '1': {},
        adFilter: 'yabs.NzIwNTc2MDQ0NTA5MDQ0NTU=',
        bannerFlags: '',
        bannerIds: [
            '72057604450904455'
        ],
        blockId: 'R-I-674114-1',
        height: '180',
        intersectionVisibility: '1',
        limit: '1',
        linkTail: 'https://an.yandex.ru/tgo/tail',
        name: 'adaptive0418',
        viewNotices: [],
        width: '1456'
    };
    const rtbMetaSettings: Partial<Req3Server> = {
        linkTail: 'https://an.yandex.ru/rtbCount/tail',
        viewNotices: [
            'https://an.yandex.ru/count/count_1'
        ],
        bannerIds: [
            6561502500
        ],
        mrcImpressions: [
            'https://yabs.yandex.ru/tracking/mrcImpressions1',
            'https://yabs.yandex.ru/tracking/mrcImpressions2'
        ],
        measurers: {
            weborama: {
                aap: 21,
                hitlogid: '3046634730863752911',
                account: 22,
                tte: 23
            },
            adloox: {
                hitlogid: '3046634730863752911',
                id5: '9167125079',
                id10: 'test2',
                creatype: '2',
                tagid: '880',
                id7: '56963047',
                id9: '3046634730863752911',
                id1: 'yandex.ru',
                id2: '52468215'
            }
        },
    };
    const mockDirectAd: Partial<Req3Server> = {
        data: { ...mockAbstractDirectData, settings: tgoSettings },
        processed: 1,
        show: 1
    };
    const mockBanners: Partial<Req3Server> = {
        banners: {
            media: {
                banner_id: 3493606,
                bnCounts: [
                    'http://awaps.yandex.ru/bnCount_1'
                ],
                click_url: 'http://awaps.yandex.ru/click',
                height: 90,
                hidpi_image: 'http://awaps.yandex.ru/hidpi_image',
                html5_iframe_src: 'http://awaps.yandex.ru/html5_iframe_src',
                image: 'http://awaps.yandex.ru/image',
                image_alt: 'Приходи 9 сентября и участвуй в конкурсе Цветочный джем рядом с домом! ',
                not_show_stat_url: 'http://awaps.yandex.ru/not_show_stat_url',
                pl_priority: 2,
                source: 'html5_hidpi_desktop_banner',
                stat_delay_sec: 2,
                width: 728
            }
        }
    };
    const mockBannersOptions: Partial<Req3Server> = {
        options: {
            ad_place: '1',
            ad_type: 'banner',
            height: '90',
            width: '728'
        }
    };
    const mockStatpixel: Partial<Req3Server> = {
        banners: {
            media: {
                banner_id: 0,
                bnCounts: [
                    'http://awaps.yandex.ru/bnCount_1'
                ],
                not_show_stat_url: 'http://awaps.yandex.ru/not_show_stat_url',
                pl_priority: 0,
                source: 'media',
                stat_delay_sec: 2
            }
        }
    };
    const mockStatpixelOptions: Partial<Req3Server> = {
        options: {
            ad_place: '0',
            ad_type: 'stat_pixel',
            height: '0',
            width: '0'
        }
    };
    const mockRtbmetaRtbDesktopImage: Partial<Req3Server> = {
        data: {
            rtb: {
                url: '',
                basePath: 'https://storage.mds.yandex.net/get-canvas-html5/1003119/bf1f886a-e526-4c09-941f-80679eac8854/',
                height: 90,
                width: 728,
                clickUrl: 'clickUrl',
                posterSrc: 'https://storage.mds.yandex.net/get-canvas-html5/1003119/bf1f886a-e526-4c09-941f-80679eac8854/image.jpg',
                html: ''
            },
            visibilitySettings: {
                delay: 2000
            },
            settings: rtbMetaSettings
        }
    };
    const mockRtbmetaRtbDesktopIframe: Partial<Req3Server> = {
        data: {
            rtb: {
                url: '',
                basePath: 'https://storage.mds.yandex.net/get-canvas-html5/1003119/bf1f886a-e526-4c09-941f-80679eac8854/',
                height: 90,
                width: 728,
                clickUrl: 'clickUrl',
                html: '<HTML 5 RTB content>'
            },
            visibilitySettings: {
                delay: 2000
            },
            settings: rtbMetaSettings
        }
    };
    const mockRtbmetaDirect: Partial<Req3Server> = {
        data: { ...mockAbstractDirectData, settings: rtbMetaSettings },
        processed: 1,
        show: 1
    };
    const mockRtbmetaEmpty: Partial<Req3Server> = {
        data: {
            common: {
                reloadTimeout: '30'
            }
        },
        processed: 1,
        show: 1
    };

    let savedMathRandom = Math.random;
    let enabledExps: {[key: string]: boolean} = {};

    beforeEach(function() {
        Math.random = function() {
            return 0;
        };
    });

    afterEach(function() {
        Math.random = savedMathRandom;

        enabledExps = {};
    });

    type TestCallback = () => void | {[key: string]: any};

    function runBannerTest(callback: TestCallback) {
        const directAdFirstlook = JSON.parse(JSON.stringify(mockDirectAd));
        const directAd = JSON.parse(JSON.stringify(mockDirectAd));
        const Banners = JSON.parse(JSON.stringify(mockBanners));
        const bannersOptions = JSON.parse(JSON.stringify(mockBannersOptions));
        const RTBMeta = {
            show: 0,
            processed: 1
        };
        const ads = new Ads({});

        const req = mockReq({}, {
            Banners_pages: '123',
            BannersRefresh: {
                overlapping_timeout: 111,
                refresh_counts: 222,
                tab_timeout: 333,
                watch_timeout: 444
            },
            Retpath: 'yandex.ru/?test=123',
            BannersMeasurers: {
                adloox: {
                    stable_version: 67,
                    unstable_version: 67
                },
                moat: {
                    stable_version: 67,
                    unstable_version: 67
                },
                weborama: {
                    stable_version: 67,
                    unstable_version: 67
                }
            },
            JSON: {
                common: {
                    pageName: 'index'
                }
            },
            Direct_ad_firstlook: directAdFirstlook,
            Direct_ad: directAd,
            Banners_awaps: bannersOptions,
            Banners,
            ads,
            RTBMeta
        });

        const banners = callback();

        if (banners) {
            for (const name in banners) {
                if (banners.hasOwnProperty(name)) {
                    req[name] = banners[name];
                }
            }
        }

        (ads as any)._banners = req.Banners.banners;
        (ads as any)._awapsOpts = req.Banners_awaps.options;

        const html = execView(BBanner, {}, req);

        return {
            html,
            resources: req.resources.add.mock.calls,
            settingsJs: req.settingsJs.add.mock.calls
        };
    }

    it('firstlook + awaps marketing', function() {
        const res = runBannerTest(function() {
            const Banners = JSON.parse(JSON.stringify(mockBanners));

            Banners.banners.media.pl_priority = 3;

            return {
                Banners
            };
        });

        expect(res).toMatchSnapshot();
    });

    it('firstlook + statpixel', function() {
        const res = runBannerTest(function() {
            return {
                Banners: JSON.parse(JSON.stringify(mockStatpixel)),
                Banners_awaps: JSON.parse(JSON.stringify(mockStatpixelOptions))
            };
        });

        expect(res).toMatchSnapshot();
    });

    it('rtbmeta-image + statpixel', function() {
        enabledExps.meta_rtb = true;

        const res = runBannerTest(function() {
            return {
                RTBMeta: JSON.parse(JSON.stringify(mockRtbmetaRtbDesktopImage)),
                Banners: JSON.parse(JSON.stringify(mockStatpixel)),
                Banners_awaps: JSON.parse(JSON.stringify(mockStatpixelOptions)),
                Direct_ad_firstlook: null
            };
        });

        expect(res).toMatchSnapshot();
    });

    it('rtbmeta-image[antiadblock] + statpixel', function() {
        enabledExps.meta_rtb = true;

        const res = runBannerTest(function() {
            return {
                antiadb_desktop: 1,
                RTBMeta: JSON.parse(JSON.stringify(mockRtbmetaRtbDesktopImage)),
                Banners: JSON.parse(JSON.stringify(mockStatpixel)),
                Banners_awaps: JSON.parse(JSON.stringify(mockStatpixelOptions)),
                Direct_ad_firstlook: null
            };
        });

        expect(res).toMatchSnapshot();
    });

    it('rtbmeta-iframe + statpixel', function() {
        enabledExps.meta_rtb = true;

        const res = runBannerTest(function() {
            return {
                RTBMeta: JSON.parse(JSON.stringify(mockRtbmetaRtbDesktopIframe)),
                Banners: JSON.parse(JSON.stringify(mockStatpixel)),
                Banners_awaps: JSON.parse(JSON.stringify(mockStatpixelOptions)),
                Direct_ad_firstlook: null
            };
        });

        expect(res).toMatchSnapshot();
    });

    it('rtbmeta-iframe[antiadblock] + statpixel', function() {
        enabledExps.meta_rtb = true;

        const res = runBannerTest(function() {
            return {
                antiadb_desktop: 1,
                RTBMeta: JSON.parse(JSON.stringify(mockRtbmetaRtbDesktopIframe)),
                Banners: JSON.parse(JSON.stringify(mockStatpixel)),
                Banners_awaps: JSON.parse(JSON.stringify(mockStatpixelOptions)),
                Direct_ad_firstlook: null
            };
        });

        expect(res).toMatchSnapshot();
    });

    it('rtbmeta-direct + statpixel', function() {
        enabledExps.meta_rtb = true;

        const res = runBannerTest(function() {
            return {
                RTBMeta: JSON.parse(JSON.stringify(mockRtbmetaDirect)),
                Banners: JSON.parse(JSON.stringify(mockStatpixel)),
                Banners_awaps: JSON.parse(JSON.stringify(mockStatpixelOptions)),
                Direct_ad_firstlook: null,
                Direct_ad: null
            };
        });

        expect(res).toMatchSnapshot();
    });

    it('rtbmeta-empty + statpixel', function() {
        enabledExps.meta_rtb = true;

        const res = runBannerTest(function() {
            return {
                RTBMeta: JSON.parse(JSON.stringify(mockRtbmetaEmpty)),
                Banners: JSON.parse(JSON.stringify(mockStatpixel)),
                Banners_awaps: JSON.parse(JSON.stringify(mockStatpixelOptions)),
                Direct_ad_firstlook: null,
                Direct_ad: null
            };
        });

        expect(res).toMatchSnapshot();
    });
});
