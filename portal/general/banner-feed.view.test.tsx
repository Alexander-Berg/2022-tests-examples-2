import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';

describe('banner-feed', function() {
    let req = mockReq({}, {
        BannerFeed: {
            data: {
                banner_feed_1: {
                    height: 300,
                    'imp-id': 'N-I-534228-3'
                },
                banner_feed_2: {
                    height: 201,
                    'imp-id': 'N-I-534228-33',
                },
                banner_feed_3: {
                    height: 201,
                    'imp-id': 'N-I-534228-33',
                },
                banner_feed_4: {
                    height: 201,
                    'imp-id': 'N-I-534228-33',
                }
            },
            processed: 1,
            show: 1
        },
        blocks_layout_ext: [
            {
                id: 'directfeed',
                layout_item: {
                    footer: 'Все предложения',
                    footer_url: 'https://yandex.ru/search/touch/direct/?from=home&source=yandex_portal&vcards=1&vhome=1&text=Объявления',
                    icon: 'direct0',
                    id: 'directfeed',
                    is_adv: '1',
                    subtitle: 'Персональные предложения',
                    title: 'Яндекс.Директ',
                    title_url: '//direct.yandex.ru/?partner'
                }
            },
            {
                id: 'directfeed_2',
                layout_item: {
                    footer: 'Все предложения',
                    footer_url: 'https://yandex.ru/search/touch/direct/?from=home&source=yandex_portal&vcards=1&vhome=1&text=Объявления',
                    icon: 'direct0',
                    id: 'directfeed_2',
                    is_adv: '1',
                    subtitle: 'Персональные предложения'
                }
            },
            {
                id: 'directfeed_3',
                layout_item: {
                    icon: 'direct0',
                    id: 'directfeed_3',
                    is_adv: '1',
                    subtitle: 'Персональные предложения'
                }
            },
            {
                id: 'directfeed_4',
                layout_item: {
                    footer: 'Все предложения',
                    footer_url: 'https://yandex.ru/search/touch/direct/?from=home&source=yandex_portal&vcards=1&vhome=1&text=Объявления',
                    id: 'directfeed_4',
                    is_adv: '1',
                    subtitle: 'Персональные предложения',
                    title: 'Яндекс.Директ',
                    title_url: '//direct.yandex.ru/?partner'
                }
            }
        ],
        JSON: {
            common: {
                pageName: 'index'
            }
        },
        options: {}
    });

    it('banner-feed_1', function() {
        expect(execView('banner-feed_1', {}, req)).toMatchSnapshot();
    });

    it('banner-feed_2', function() {
        expect(execView('banner-feed_2', {}, req)).toMatchSnapshot();
    });

    it('banner-feed_3', function() {
        expect(execView('banner-feed_3', {}, req)).toMatchSnapshot();
    });

    it('banner-feed_4', function() {
        expect(execView('banner-feed_4', {}, req)).toMatchSnapshot();
    });
});
