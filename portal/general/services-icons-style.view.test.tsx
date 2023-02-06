import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { ServicesIconsStyle } from '@block/services-icons-style/services-icons-style.view';

describe('services-icons-styles', function() {
    let mockData = [
        {
            mod: 'small',
            services: [
                [
                    {
                        icon_id: 'avia',
                        id: 'avia'
                    },
                    {
                        icon_id: 'bus',
                        id: 'bus'
                    }
                ],
                [
                    {
                        icon_id: 'avia',
                        id: 'avia'
                    },
                    {
                        icon_id: 'bus',
                        id: 'bus'
                    }
                ]
            ],
            folder: 'small'
        },
        {
            mod: 'big',
            services: [
                [
                    {
                        all_group: 'searchBlock',
                        icon: 'https://yastatic.net/s3/home/icon_services/avia2.png',
                        icon_id: 'avia',
                        id: 'avia',
                        title: 'Авиабилеты',
                        url: 'https://avia.yandex.ru/?utm_source=yamain&utm_medium=allservices&utm_campaign=avia_ru'
                    },
                    {
                        all_group: 'searchBlock',
                        icon: 'https://yastatic.net/s3/home/icon_services/bus.png',
                        icon_id: 'bus',
                        id: 'bus',
                        title: 'Автобусы',
                        url: 'https://yandex.ru/bus?utm_source=yamain&utm_medium=allservices_ru&utm_campaign=main'
                    }
                ]
            ],
            folder: 'big'
        }
    ];
    let reqSvg = mockReq({}, {
        BrowserDesc: {
            BrowserBase: 'Chromium',
            BrowserBaseVersion: '81.0.4044.113',
            BrowserEngine: 'WebKit',
            BrowserEngineVersion: '537.36',
            BrowserName: 'Chrome',
            BrowserVersion: '81.0.4044.113',
            CSP1Support: 1,
            CSP2Support: 1,
            OSFamily: 'MacOS',
            OSName: 'macOS Catalina',
            OSVersion: '10.15.4',
            SVGSupport: 1,
            SameSiteSupport: 1,
            WebPSupport: 1,
            historySupport: 1,
            isBrowser: 1,
            isMobile: 0,
            isTouch: 0,
            localStorageSupport: 1,
            postMessageSupport: 1
        }
    });
    let reqPng = mockReq({}, {
        BrowserDesc: {
            isTouch: 0,
            BrowserVersion: '12.16',
            BrowserEngine: 'Presto',
            SVGSupport: 1,
            WebPSupport: 1,
            isBrowser: 1,
            historySupport: 1,
            BrowserEngineVersion: '2.12.388',
            OSVersion: '10.15.4',
            BrowserName: 'Opera',
            postMessageSupport: 1,
            localStorageSupport: 1,
            OSFamily: 'MacOS',
            OSName: 'macOS Catalina',
            isMobile: 0
        }
    });

    let resSvg = execView(ServicesIconsStyle, mockData, reqSvg);
    let resPng = execView(ServicesIconsStyle, mockData, reqPng);

    /* eslint-disable max-len*/
    let etalonSvg = '<style  >' +
            '.avia_small{' +
            'background-image: url(//yastatic.net/s3/home/services/all/svg/avia.svg);' +
            '}' +
            '.bus_small{' +
            'background-image: url(//yastatic.net/s3/home/services/all/svg/bus.svg);' +
            '}' +
            '</style>' +
            '<style  >' +
            '.avia_big{' +
            'background-image: url(//yastatic.net/s3/home/services/all/svg/avia.svg);' +
            '}' +
            '.bus_big{' +
            'background-image: url(//yastatic.net/s3/home/services/all/svg/bus.svg);' +
            '}' +
            '</style>';
    let etalonPng = '<style  >' +
            '.avia_small{' +
            'background-image: url(//yastatic.net/s3/home/services/all/small_png/avia.png);' +
            '}' +
            '.bus_small{' +
            'background-image: url(//yastatic.net/s3/home/services/all/small_png/bus.png);' +
            '}' +
            '</style>' +
            '<style  >' +
            '.avia_big{' +
            'background-image: url(//yastatic.net/s3/home/services/all/big_png/avia.png);' +
            '}' +
            '.bus_big{' +
            'background-image: url(//yastatic.net/s3/home/services/all/big_png/bus.png);' +
            '}' +
            '</style>';

    it('svg', function() {
        expect(resSvg).toEqual(etalonSvg);
    });

    it('png', function() {
        expect(resPng).toEqual(etalonPng);
    });
});
