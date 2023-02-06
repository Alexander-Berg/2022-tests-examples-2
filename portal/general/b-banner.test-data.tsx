/* eslint-env es6 */
import { mockReq } from '@lib/views/mockReq';
import { execView } from '@lib/views/execView';
import { Ads } from '@lib/utils/ads';
import * as tgo from '@block/direct/mocks/tgo.json';
import { BBanner } from './b-banner.view';

const imgBase = 'https://mmui-png-stub.yandex-team.ru/?strategy=pngPatternStub&borderColor=red';
const rowStyle = '<style>.row {padding: 10px; display: inline-block}</style>';
const iPerformanceHack = 'window.PerformanceObserver = null;';
const rumStub = 'window.Ya = window.Ya || {};window.Ya.Rum = window.Ya.Rum || {};window.Ya.Rum.send = window.Ya.Rum.send || function(){};';
const thisMockBase = '?datafile=white/blocks/bender/b-banner/b-banner.test-data.tsx';
const adbImage = 'https://yastatic.net/s3/home/garry_test_img/banner_test.png';
const rtbImage = adbImage;
const yabsLoImg = `${imgBase}&for=yabsLo&w=1456&h=180&color=rgb(0,128,255)`;
const yabsHiImg = `${imgBase}&for=yabsHi&w=1456&h=180&color=rgb(0,0,255)`;

const noBannerReq: Partial<Req3Server> = {
    Banners_pages: '123',
    Banners: {}
};

const yabsReq: Partial<Req3Server> = {
    Banners: {
        banners: {
            banner: {
                ad_nmb: '72057605002383905',
                bnCounts: [`${thisMockBase}&dataname=counter&counts`],
                click_url: `${thisMockBase}&dataname=counter#yabsclick`,
                height: 90,
                hidpi_image: yabsHiImg,
                html5_iframe_src: '',
                image: yabsLoImg,
                image_alt: 'Ехать, отправлять, встречать. Яндекс Go. 0+',
                width: 728
            } as Req3BannerYabs
        }
    }
};
const direct: {data: TgoData} = {
    data: {
        common: {
            linkHead: `${thisMockBase}&dataname=counter`
        },
        settings: {
            bannerIds: ['1'],
            '1': {
            }
        },
        direct: {
            directTitle: {
                title: 'Direct Title',
                url: '#direct-url'
            },
            ads: [{ ...tgo.ad, ...{ url: `${thisMockBase}&dataname=counter#directclick` } } as unknown as DirectDataAd]
        }
    }
};
const rtbMetaExpReq: Partial<Req3Server> = {
    meta_rtb: {
        exp: {
            content: 'big',
            domain: 'kubru',
            exp_slot: '0',
            from: '2019-03-26',
            geos: '10000',
            id: 'meta_rtb',
            info: 'новая ручка рекламы. десктоп',
            new_yuid: '1',
            percent: '20',
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
};
const rtbMetaSettingsReq: DirectSettings = {
    linkTail: '/empty?counter=RtbCounter',
    viewNotices: [`${thisMockBase}&dataname=counter&view`] as string[],
    bannerIds: [
        '6561502500'
    ]
};
const metaRtbDirectReq: Partial<Req3Server> = {
    exp: rtbMetaExpReq as Req3Server['exp'],
    RTBMeta: {
        data: {
            common: direct.data.common,
            direct: direct.data.direct,
            settings: rtbMetaSettingsReq
        },
        processed: 1,
        show: 1
    }
};
const metaRtbImageReq: Partial<Req3Server> = {
    exp: rtbMetaExpReq as Req3Server['exp'],
    RTBMeta: {
        data: {
            rtb: {
                url: `${thisMockBase}#rtbclick`,
                basePath: 'https://storage.mds.yandex.net/get-canvas-html5/1003119/bf1f886a-e526-4c09-941f-80679eac8854/',
                height: 180,
                width: 1456,
                clickUrl: `${thisMockBase}#rtbclick`,
                posterSrc: rtbImage,
                abuseLink: '//an.yandex.ru/abuse/W9qejI_z8Asb103a1tyYSoLxwyZ_1G2j035maJ1W000003YifL9mpFF2suqYa06Ix-VFp820W0AO0PBlvyzCs06YcVMN0UW1i06W0jRg1Ca6RIlthiSeFawT3wuWTtJHpGc82mog2n16vMMw3wu00DSHFnUzkmK0s1N1YlRieu-y_6E15_0_-1Y06GO0BWNZB8GD6RxkYnsqOsm9C7q6~1'
            },
            visibilitySettings: {
                delay: 2000
            },
            settings: rtbMetaSettingsReq
        },
        processed: 1,
        show: 1
    }
};
const metaRtbSocialReq: Partial<Req3Server> = {
    RTBMeta: {
        data: {
            rtb: {
                url: `${thisMockBase}#rtbclick`,
                basePath: 'https://storage.mds.yandex.net/get-canvas-html5/1003119/bf1f886a-e526-4c09-941f-80679eac8854/',
                height: 180,
                width: 1456,
                clickUrl: `${thisMockBase}#rtbclick`,
                posterSrc: rtbImage,
                abuseLink: '//an.yandex.ru/abuse/W9qejI_z8Asb103a1tyYSoLxwyZ_1G2j035maJ1W000003YifL9mpFF2suqYa06Ix-VFp820W0AO0PBlvyzCs06YcVMN0UW1i06W0jRg1Ca6RIlthiSeFawT3wuWTtJHpGc82mog2n16vMMw3wu00DSHFnUzkmK0s1N1YlRieu-y_6E15_0_-1Y06GO0BWNZB8GD6RxkYnsqOsm9C7q6~1'
            },
            visibilitySettings: {
                delay: 2000
            },
            settings: {
                ...rtbMetaSettingsReq,
                bannerFlags: 'animated,social_advertising'
            }
        },
        processed: 1,
        show: 1
    }
};
const metaRtbIframeReq: Partial<Req3Server> = {
    exp: rtbMetaExpReq as Req3Server['exp'],
    RTBMeta: {
        data: {
            rtb: {
                url: `${thisMockBase}#rtbclick`,
                abuseLink: '//an.yandex.ru/abuse/W9qejI_z8Asb103a1tyYSoLxwyZ_1G2j035maJ1W000003YifL9mpFF2suqYa06Ix-VFp820W0AO0PBlvyzCs06YcVMN0UW1i06W0jRg1Ca6RIlthiSeFawT3wuWTtJHpGc82mog2n16vMMw3wu00DSHFnUzkmK0s1N1YlRieu-y_6E15_0_-1Y06GO0BWNZB8GD6RxkYnsqOsm9C7q6~1',
                basePath: 'https://storage.mds.yandex.net/get-canvas-html5/1003119/bf1f886a-e526-4c09-941f-80679eac8854/',
                height: 180,
                width: 1456,
                clickUrl: `${thisMockBase}#rtbclick`,
                html: '',
                indexSrc: `${thisMockBase}&dataname=rtbFrame`
            },
            visibilitySettings: {
                delay: 2000
            },
            settings: rtbMetaSettingsReq
        },
        processed: 1,
        show: 1
    }
};
const directFirstlookReq: Partial<Req3Server> = {
    Direct_ad_firstlook: direct
};

const statMock = `<script src="/node_modules/sinon/pkg/sinon.js"></script>
<script>
    window.logPathSpy = sinon.spy(home.stat, 'logPath');
</script>`;

const ioMock = `
<script>
    window.IntersectionObserver = function(cb){
        this.cb = cb;
    }
    window.IntersectionObserver.prototype.observe = function(elem){
        setTimeout(function(){
            this.cb([{intersectionRatio: 1}]);
        }.bind(this), 0);
    };
    window.IntersectionObserver.prototype.unobserve = function(elem){};
</script>
`;

const markIframeLoaded = `
<script>
    BEM.channel('adb').on('rendered', function (event, data) {
        data.elem.addEventListener('load', function() {
            window.iframeLoaded = true;
        });
    });
</script>
`;

function get(mock: Partial<Req3Server>): () => unknown {
    const settingsJs = home.settingsJs([]);
    const ads = new Ads(mock);
    const req: Req3Server = mockReq({}, {
        settingsJs,
        JSON: {
            common: {}
        },
        options: {},
        ads,
        ...mock
    });

    req.resources = new home.Resources('white', req, execView);
    req.resources.addBundle = () => '';

    let banner = execView(BBanner, {}, req);

    return () => {
        const imageClass = req.JSON?.bannerAdbImgSearch || '';
        const html = `
            ${rowStyle}
            ${req.resources.getHTML('head')}
            <script>${settingsJs.getRawScript(req)}</script>
            ${statMock}
            ${ioMock}
            <div class="row test-container b-banner__content rtb-border ${imageClass}" style="width:780px; height: 92.6px; position: relative">${banner}</div>
            ${req.resources.getHTML('body')}
            ${markIframeLoaded}`;

        const mockJs = `${settingsJs.getRawScript(req)}
                        ${rumStub}
                        ${iPerformanceHack}`;

        return { html, mockJs };
    };
}

export const noBanner = get(noBannerReq);
export const yabs = get({ ...noBannerReq, ...yabsReq });
export const directFirstlook = get(directFirstlookReq);
export const directBackfillStatpixel = get(metaRtbDirectReq);
export const metaRtbDirect = get(metaRtbDirectReq);
export const metaRtbImage = get(metaRtbImageReq);
export const metaRtbSocial = get(metaRtbSocialReq);
export const metaRtbIframe = get(metaRtbIframeReq);
export function counter() {
    return '<body><script>document.write("this is " + location.hash);document.close()</script><body>';
}

export function rtbFrame() {
    return `<style>
    .text {
        display: block;
        text-decoration: none;
        color: #000;
        height: 100%;
        text-align: center;
        background: url("${imgBase}&w=918&h=113&for=frame&color=rgb(190,200,190)") 50% 0/100% auto;
    }
    </style>
    <a href="${thisMockBase}&dataname=counter#rtbframeclick" target="_blank" class="text">rtb frame</a>`;
}
