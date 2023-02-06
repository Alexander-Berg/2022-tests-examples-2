'use strict';

const PAGEDATA = {
    url: {
        path: '/efir',
        getParams: {
            blogger: {
                stream_active: 'blogger',
                stream_publisher: 'voditem_channel_id_4ca3583da58eb67cb6aa97344a201008',
                exp: 'stream_publisher'
            },
            channelsList: {
                stream_active: 'channels-list'
            },
            schedule: {
                stream_active: 'schedule',
                stream_channel: 161
            },
            watchingChannel: {
                stream_channel: 161
            },
            watchingFilm: {
                stream_id: '48ffe97c31358d728c51d050ea2740f4'
            },
            watchingSeries: {
                stream_id: '41c2aab62bc8b154b4b03bdf8cb74157'
            },
            categoryFilm: {
                stream_active: 'category',
                stream_category: 'film',
                geo: 225
            },
            categorySeries: {
                stream_active: 'category',
                stream_category: 'series',
                geo: 225
            }
        }
    },
    classNames: {
        stream: '.stream',
        screens: {
            '404': '.stream-404',
            channelsList: '.stream-channels-list',
            schedule: '.stream-schedule',
            watching: '.stream-watching',
            category: '.stream-category',
            blogger: '.stream-blogger',
            storefront: '.stream-storefront',
            errorRegion: '.stream-error-region',
            sidemenu: '.stream-sidemenu'
        },
        active: {
            blogger: '.stream_blogger_active',
            storefront: '.stream_storefront_active',
            channelsList: '.stream_channels-list_active',
            schedule: '.stream_schedule_active',
            watching: '.stream_watching_active',
            category: '.stream_category_active'
        },
        blogger: {
            header: '.stream-landing-header',
            topImage: '.stream-landing-header__top',
            headerInfo: '.stream-landing-header__header-info',
            items: '.stream-blogger__items'
        },
        watching: {
            player: '.stream-watching__player',
            doc2docReact: '.Doc2doc',
            doc2doc: '.stream-watching__container-doc2doc',
            schedule: '.stream-watching__schedule',
            main: '.stream-watching__main',
            channels: '.stream-watching__channels',
            footer: '.stream-watching__footer',
            series: '.stream-series-navigator'
        },
        category: {
            feed: '.stream-feed',
            carousels: '.stream-category__carousels',
            header: '.stream-category__header',
            items: '.stream-category__items'
        },
        channelsList: {
            categories: '.stream-channels-list__categories',
            content: '.stream-channels-list__content'
        },
        schedule: {
            channelHeader: '.stream-schedule__channel-header',
            calendar: '.stream-schedule__calendar',
            events: '.stream-schedule__events',
            link: '.stream-schedule__link'
        },
        streamEvents: {
            className: '.stream-events',
            item: '.stream-events__item'
        },
        taglist: {
            className: '.taglist',
            itemKey: '.taglist__item-key',
            itemContent: '.taglist__item-content'
        },
        header: {
            bottom: '.stream-header__bottom',
            categories: '.stream-header__categories',
            searchInput: '.stream-search input',
            tabs: {
                item: '.stream-header__categories-item',
                channels: '.stream-header__categories-item_section_channels-list',
                active: '.stream-header__categories-item_current_yes',
                blogger: '.stream-header__categories-item_section_blogger'
            }
        },
        sidemenu: {
            toggles: '.stream-sidemenu__toggles',
            channels: '.stream-sidemenu__channels',
            blocks: '.stream-sidemenu__blocks'
        },
        storefront: {
            top: '.stream-storefront__top',
            feed: '#stream-storefront__feed',
            embed: '.stream-storefront__player-wrapper'
        }
    },
    mocks: {
        regionError: '5ce3c056dcbace8ca55fc629'
    }
};

const getClassName = function (selector) {
    return selector.split('.')[0];
};

module.exports = {
    PAGEDATA,
    getClassName
};
