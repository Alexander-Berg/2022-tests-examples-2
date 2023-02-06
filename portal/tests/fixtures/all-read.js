module.exports = function() {
    return {
        uid: '',
        ticker: {
            unviewed_count: 1,
            show_style: '',
            services: {},
            reset_time: '2021-08-31T16:34:33.396634Z',
        },
        services: [
            {
                id: 'fakeservice',
                name: {
                    ru: 'Я.Чудесный дамп',
                },
                icon_src: '//yastatic.net/iconostasis/_/8lFaTHLDzmsEZz-5XaQg9iTWZGE.png',
                show_group: {},
                blocks: [
                    {
                        id: 'rcnt0',
                        message: {
                            ru: {
                                text: 'Здесь короткая страница без дзена',
                                meta: JSON.stringify({}),
                            },
                        },
                        action: 'action',
                        actor: 'actor',
                        preview: 'preview',
                        meta: JSON.stringify({
                            action: {
                                link: 'https://ya.ru',
                            },
                            actor: {},
                            preview: {},
                        }),
                        type: 'fake',
                        mtime: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
                        is_read: true,
                        is_new: true,
                    },
                    {
                        id: 'rcnt1',
                        message: {
                            ru: {
                                text: 'Здесь ещё страница без дзена',
                                meta: JSON.stringify({}),
                            },
                        },
                        action: 'action',
                        actor: 'actor',
                        preview: 'preview',
                        meta: JSON.stringify({
                            action: {
                                link: 'https://ya.ru',
                            },
                            actor: {},
                            preview: {},
                        }),
                        type: 'fake',
                        mtime: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
                        is_read: true,
                        is_new: false,
                    },
                    {
                        id: 'rcnt2',
                        message: {
                            ru: {
                                text: 'Здесь страница поиска',
                                meta: JSON.stringify({}),
                            },
                        },
                        action: 'action',
                        actor: 'actor',
                        preview: 'preview',
                        meta: JSON.stringify({
                            action: {
                                link: 'https://ya.ru',
                            },
                            actor: {},
                            preview: {},
                        }),
                        type: 'fake',
                        mtime: new Date(Date.now() - 61 * 60 * 1000).toISOString(),
                        is_read: true,
                        is_new: false,
                    },
                ],
            },
            {
                id: 'fakeservice2',
                name: {
                    ru: 'Я.Чудесный мок',
                },
                icon_src: '//yastatic.net/s3/home/services/all/svg/autoru0.svg',
                show_group: {},
                blocks: [
                    {
                        id: 'rcn2t0',
                        message: {
                            ru: {
                                text: 'Здесь короткая страница без дзена',
                                meta: JSON.stringify({}),
                            },
                        },
                        action: 'action',
                        actor: 'actor',
                        preview: 'preview',
                        meta: JSON.stringify({
                            action: {
                                link: 'https://ya.ru',
                            },
                            actor: {},
                            preview: {},
                        }),
                        type: 'fake',
                        mtime: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
                        is_read: true,
                        is_new: true,
                    },
                    {
                        id: 'rcn2t1',
                        message: {
                            ru: {
                                text: 'Здесь ещё страница без дзена',
                                meta: JSON.stringify({}),
                            },
                        },
                        action: 'action',
                        actor: 'actor',
                        preview: 'preview',
                        meta: JSON.stringify({
                            action: {
                                link: 'https://ya.ru',
                            },
                            actor: {},
                            preview: {},
                        }),
                        type: 'fake',
                        mtime: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
                        is_read: true,
                        is_new: false,
                    },
                    {
                        id: 'rcn2t2',
                        message: {
                            ru: {
                                text: 'Здесь страница поиска',
                                meta: JSON.stringify({}),
                            },
                        },
                        action: 'action',
                        actor: 'actor',
                        preview: 'preview',
                        meta: JSON.stringify({
                            action: {
                                link: 'https://ya.ru',
                            },
                            actor: {},
                            preview: {},
                        }),
                        type: 'fake',
                        mtime: new Date(Date.now() - 70 * 60 * 1000).toISOString(),
                        is_read: true,
                        is_new: false,
                    },
                ],
            },
        ],
        context: {
            omit_notification_sort: false,
            exp_boxes: '400816,0,-1',
        },
        reqid: 'rdcwthuppnaydjex.sas.yp-c.yandex.net:80-1629288667-286354455',
    };
};
