module.exports = function() {
    return req([
        service({
            name: 'Я.Антивирус',
            id: 'fakeservice0',
            blocks: [
                block({ id: 'rcnt0', text: 'Доступно 123 новых обновления' }),
                block({ id: 'rcnt1', text: 'Найдено 123 вируса' }),
                block({ id: 'rcnt2', text: 'Можно освободить 123ГБ на жестком диске' }),
                block({ id: 'rcnt3', text: 'Производительность компьютера выросла на 20% после Я.Чистки' }),
            ],
        }),
        service({
            name: 'Я.Чистка',
            id: 'fakeservice1',
            blocks: [
                block({ id: 'rcnt4', text: 'Экран протетр' }),
                block({ id: 'rcnt5', text: 'Кулеры продуты' }),
                block({ id: 'rcnt6', text: 'Обои поменяны' }),
                block({ id: 'rcnt7', text: 'Биткоин замайнен' }),
                block({ id: 'rcnt8', text: '123 пароля было изменено' }),
                block({ id: 'rcnt9', text: 'ОШИБКА' }),
            ],
        }),
        service({
            name: 'Я.Одинок',
            id: 'fakeservice2',
            blocks: [
                block({ id: 'rcnt10', text: 'Уведомление без друзей :с' }),
            ],
        }),
    ]);
};

const req = services => ({
    uid: '',
    ticker: {
        unviewed_count: 1,
        show_style: '',
        services: {},
        reset_time: '2021-08-31T16:34:33.396634Z',
    },
    services,
    context: {
        omit_notification_sort: false,
        exp_boxes: '400816,0,-1',
    },
    reqid: 'rdcwthuppnaydjex.sas.yp-c.yandex.net:80-1629288667-286354455',
});

const service = ({ id, name, blocks }) => ({
    id,
    name: {
        ru: name,
    },
    icon_src: '//yastatic.net/iconostasis/_/8lFaTHLDzmsEZz-5XaQg9iTWZGE.png',
    show_group: {
        qwe: {
            text: 'olole',
            enabled: true,
        },
    },
    blocks,
});

const block = ({
    id,
    text,
    is_read = false,
    is_new = true,
    preview = 'https://yastatic.net/s3/home-static/_/37/37a02b5dc7a51abac55d8a5b6c865f0e.png',
}) => ({
    id,
    message: {
        ru: {
            text,
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
            preview,
        },
    }),
    type: 'fake',
    mtime: new Date(new Date().setHours(12, 0, 0, 0) - 30 * 1000 - 5 * 60 * 1000).toISOString(),
    is_read,
    is_new,
});
