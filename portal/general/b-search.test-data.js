exports.simple = function (execView) {
    return '<div class="center">' + execView('BSearch', {}, {
        'ShowID': '1.2.3.4',
        'Services_tabs': {
            'show': 4,
            'processed': 1,
            'list': [
                {
                    'tabs_tablet': '2',
                    'search': '//yandex.com/images/search?text=',
                    'search_mobile': 'https://yandex.com/images/touch/search',
                    'android': '1',
                    'tabs_touch': '1',
                    'bada': '1',
                    'domain': 'com',
                    'href': 'https://yandex.com/images/smart',
                    'url': '//yandex.com/images',
                    'id': 'images',
                    'search_tablet': '//yandex.com/images/search?text=',
                    'iphone': '1',
                    'tabs': '2',
                    'pda': 'https://yandex.com/images/smart',
                    'api_search': '10',
                    'wp': '1',
                    'touch': 'https://yandex.com/images/touch/'
                },
                {
                    'href_orig': '//yandex.com/video',
                    'tabs_tablet': '3',
                    'tabs': '3',
                    'iphone': '2',
                    'search': '//yandex.com/video/search?text=',
                    'search_mobile': '//yandex.com/video/touch/#!/search',
                    'android': '2',
                    'domain': 'com',
                    'href': '//yandex.com/video/touch/',
                    'url': '//yandex.com/video',
                    'wp': '2',
                    'touch': '//yandex.com/video/touch/',
                    'id': 'video',
                    'search_tablet': '//yandex.com/video/search?text='
                },
                {
                    'tabs': '5',
                    'iphone': '4',
                    'android': '4',
                    'tabs_touch': '4',
                    'bada': '4',
                    'domain': 'com',
                    'href': '//translate.yandex.com/',
                    'url': '//translate.yandex.com/',
                    'wp': '4',
                    'id': 'translate'
                },
                {
                    'iphone': '5',
                    'android': '5',
                    'tabs_touch': '5',
                    'domain': 'com',
                    'href': '//browser.yandex.com/',
                    'wp': '5',
                    'url': '//browser.yandex.com/',
                    'id': 'browser'
                }
            ]
        }
    }) + '</div>';
};
