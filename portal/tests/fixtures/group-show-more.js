module.exports = function() {
    return req([
        service({
            name: 'Я.Антивирус',
            id: 'fakeservice',
            blocks: [
                block({ id: 'rcnt0', text: 'Доступно 123 новых обновления', groupID: 'fakegroup' }),
                block({ id: 'rcnt1', text: 'Найдено 123 вируса', groupID: 'fakegroup' }),
                block({ id: 'rcnt2', text: 'Можно освободить 123ГБ на жестком диске', groupID: 'fakegroup' }),
                block({ id: 'rcnt3', text: 'Производительность компьютера выросла на 20% после Я.Чистки' }),
                block({ id: 'rcnt4', text: 'Был удален браузер Амиго' }),
                block({ id: 'rcnt5', text: 'Защитите свою бабукшу, подарив Я.Антивирус' }),
                block({ id: 'rcnt6', text: 'Не желаете поставить Я.Браузер?' }),
                block({ id: 'rcnt7', text: 'Обнаружен троян!!!' }),
                block({ id: 'rcnt8', text: 'Лицензия истекает через 3 дня' }),
                block({ id: 'rcnt9', text: 'Произошла утечка паролей' }),
                block({ id: 'rcnt10', text: 'Пароль password123 подходит к вашему Я.Паспорту' }),
                block({ id: 'rcnt11', text: 'Промокод AntiVir в честь дня рождения Я.Антивируса' }),
                block({ id: 'rcnt12', text: 'В два раза увеличено число ошибок' }),
                block({ id: 'rcnt13', text: 'virus.exe содержит вирус' }),
                block({ id: 'rcnt14', text: 'Самое масштабное обновление в истории' }),
                block({ id: 'rcnt15', text: 'Я.Антивирус доступен на вашем Iphone 13' }),
                block({ id: 'rcnt16', text: 'Сканирование началось.' }),
                block({ id: 'rcnt17', text: 'Провести сканирование?' }),
                block({ id: 'rcnt18', text: 'Ваш компьютер в безопасности' }),
                block({ id: 'rcnt19', text: 'Я.Антивирус активирован' }),
                block({ id: 'rcnt20', text: 'Ошибка в процессе обновления' }),
            ],
        }),
        service({
            name: 'Я.Антивирус2',
            id: 'fakeservice2',
            blocks: [
                block({ id: '1rcnt0', text: 'Доступно 123 новых обновления', groupID: 'fakegroup' }),
                block({ id: '1rcnt1', text: 'Найдено 123 вируса', groupID: 'fakegroup' }),
                block({ id: '1rcnt2', text: 'Можно освободить 123ГБ на жестком диске', groupID: 'fakegroup' }),
                block({ id: '1rcnt3', text: 'Производительность компьютера выросла на 20% после Я.Чистки' }),
                block({ id: '1rcnt4', text: 'Был удален браузер Амиго' }),
                block({ id: '1rcnt5', text: 'Защитите свою бабукшу, подарив Я.Антивирус' }),
                block({ id: '1rcnt6', text: 'Не желаете поставить Я.Браузер?' }),
                block({ id: '1rcnt7', text: 'Обнаружен троян!!!' }),
                block({ id: '1rcnt8', text: 'Лицензия истекает через 3 дня' }),
                block({ id: '1rcnt9', text: 'Произошла утечка паролей' }),
                block({ id: '1rcnt10', text: 'Пароль password123 подходит к вашему Я.Паспорту' }),
                block({ id: '1rcnt11', text: 'Промокод AntiVir в честь дня рождения Я.Антивируса' }),
                block({ id: '1rcnt12', text: 'В два раза увеличено число ошибок' }),
                block({ id: '1rcnt13', text: 'virus.exe содержит вирус' }),
                block({ id: '1rcnt14', text: 'Самое масштабное обновление в истории' }),
                block({ id: '1rcnt15', text: 'Я.Антивирус доступен на вашем Iphone 13' }),
                block({ id: '1rcnt16', text: 'Сканирование началось.' }),
                block({ id: '1rcnt17', text: 'Провести сканирование?' }),
                block({ id: '1rcnt18', text: 'Ваш компьютер в безопасности' }),
                block({ id: '1rcnt19', text: 'Я.Антивирус активирован' }),
                block({ id: '1rcnt20', text: 'Ошибка в процессе обновления' }),
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
    groupID,
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
    groupID,
});
