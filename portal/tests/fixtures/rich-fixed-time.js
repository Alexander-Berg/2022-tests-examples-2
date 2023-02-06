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
                id: 'fakeservice1',
                name: {
                    ru: 'Дзен',
                },
                icon_src: '//yastatic.net/iconostasis/_/8lFaTHLDzmsEZz-5XaQg9iTWZGE.png',
                show_group: {
                    qwe4: {
                        text: 'Обновления Дзен',
                        enabled: true,
                    },
                    qwe5: {
                        text: 'Сообщения от пользователей',
                        enabled: true,
                    },
                },
                blocks: [],
            },
            {
                id: 'fakeservice',
                name: {
                    ru: 'Я.Чудесный дамп',
                },
                icon_src: '//yastatic.net/iconostasis/_/8lFaTHLDzmsEZz-5XaQg9iTWZGE.png',
                show_group: {
                    qwe: {
                        text: 'Полезная настройка',
                        enabled: true,
                    },
                    qwe1: {
                        text: 'Другая полезная настройка',
                        enabled: true,
                    },
                    qwe2: {
                        text: 'Получать СПАМ',
                        enabled: true,
                    },
                    qw3: {
                        text: 'Не получать спам',
                        enabled: false,
                    },
                },
                blocks: [
                    {
                        id: 'rcnt0',
                        message: {
                            ru: {
                                text: 'Тут есть превью',
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
                                preview: 'https://yastatic.net/s3/home-static/_/37/37a02b5dc7a51abac55d8a5b6c865f0e.png'
                            },
                        }),
                        type: 'fake',
                        mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 5 * 60 * 1000).toISOString(),
                        is_read: false,
                        is_new: true,
                    },
                    {
                        id: 'rcnt1',
                        message: {
                            ru: {
                                text: 'Тут есть аватарка',
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
                            actor: {
                                avatar: 'https://avatars.mds.yandex.net/get-yapic/21377/enc-03e5d2c656b935040a0aae807a63eb82ab0efb114d01455b16146e2de4bc86f6'
                            },
                            preview: {},
                        }),
                        type: 'fake',
                        mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 20 * 60 * 1000).toISOString(),
                        is_read: false,
                        is_new: false,
                    },
                    {
                        id: 'rcnt21',
                        message: {
                            ru: {
                                text: 'Тут есть аватарка и аватарка, и аватарка, и аватарка, и аватарка, и река, и лес, и май.',
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
                            actor: {
                                avatar: 'https://avatars.mds.yandex.net/get-yapic/21377/enc-03e5d2c656b935040a0aae807a63eb82ab0efb114d01455b16146e2de4bc86f6'
                            },
                            preview: {},
                        }),
                        type: 'fake',
                        mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 20 * 60 * 1000).toISOString(),
                        is_read: false,
                        is_new: false,
                    },
                    {
                        id: 'rcnt2',
                        message: {
                            ru: {
                                text: 'Тут есть аватарка и превью',
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
                            actor: {
                                avatar: 'https://avatars.mds.yandex.net/get-yapic/21377/enc-03e5d2c656b935040a0aae807a63eb82ab0efb114d01455b16146e2de4bc86f6'
                            },
                            preview: {
                                preview: 'https://yastatic.net/s3/home-static/_/37/37a02b5dc7a51abac55d8a5b6c865f0e.png'
                            },
                        }),
                        type: 'fake',
                        mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 61 * 60 * 1000).toISOString(),
                        is_read: true,
                        is_new: false,
                    },
                    {
                        id: 'rcnt3',
                        message: {
                            ru: {
                                text: 'Тут есть аватарка и превью, и превью, и превью, и превью, и превью, и река, и лес, и май.',
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
                            actor: {
                                avatar: 'https://avatars.mds.yandex.net/get-yapic/21377/enc-03e5d2c656b935040a0aae807a63eb82ab0efb114d01455b16146e2de4bc86f6'
                            },
                            preview: {
                                preview: 'https://yastatic.net/s3/home-static/_/37/37a02b5dc7a51abac55d8a5b6c865f0e.png'
                            },
                        }),
                        type: 'fake',
                        mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 61 * 60 * 1000).toISOString(),
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
