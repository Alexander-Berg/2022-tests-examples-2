module.exports = function() {
    const now = new Date();

    const time = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 8, 25);

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
                id: 'fakezen',
                name: {
                    ru: 'Яндекс.Дзен',
                },
                icon_src: 'https://yastatic.net/s3/zen-lib/favicons4/favicon-32x32.png',
                show_group: {},
                blocks: [
                    {
                        id: 'rcnt0',
                        message: {
                            ru: {
                                text: 'Банк России увеличил долю золота и юаня в своих активах',
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
                            preview: {
                                preview: 'https://jing.yandex-team.ru/files/core/bell-fake-service-icon.png',
                            },
                        }),
                        type: 'fake',
                        mtime: time.toISOString(),
                        is_read: false,
                        is_new: true,
                    },
                ],
            },
            {
                id: 'fakeservice',
                name: {
                    ru: 'Яндекс',
                },
                icon_src: 'https://yastatic.net/s3/web4static/_/v2/ZcejnfbLE_TlMK13nS41mdC4A88.png',
                show_group: {},
                blocks: [
                    {
                        id: 'rcnt11',
                        message: {
                            ru: {
                                text: 'Дождь начнеться в течении часа (данные на 8:20)',
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
                        mtime: time.toISOString(),
                        is_read: false,
                        is_new: true,
                    },
                ],
            },
            {
                id: 'fakemarket',
                name: {
                    ru: 'Маркет',
                },
                icon_src: 'https://yastatic.net/s3/home/services/all/svg/market_2.svg',
                show_group: {},
                blocks: [
                    {
                        id: 'rcnt12',
                        message: {
                            ru: {
                                text: 'Заказ 51522801 создан. Мы уже начали его обрабатывать',
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
                            preview: { },
                        }),
                        type: 'fake',
                        mtime: time.toISOString(),
                        is_read: false,
                        is_new: true,
                    },
                ],
            },
            {
                id: 'fakeq',
                name: {
                    ru: 'Новый пост в сообществе «Бизнес и менеджмент»',
                },
                icon_src: 'https://yastatic.net/s3/home/services/all/svg/q0.svg',
                show_group: {},
                blocks: [
                    {
                        id: 'rcnt13',
                        message: {
                            ru: {
                                text: 'Илья Иноземцев добавил пост «3000! и конкурс»',
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
                        mtime: time.toISOString(),
                        is_read: false,
                        is_new: true,
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
