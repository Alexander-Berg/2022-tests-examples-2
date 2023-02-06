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
const service = ({ id, settings = {}, name, notifications, icon = '//yastatic.net/iconostasis/_/8lFaTHLDzmsEZz-5XaQg9iTWZGE.png' }) => ({
    id,
    name: {
        ru: name,
    },
    icon_src: icon,
    show_group: settings,
    blocks: notifications,
});
const avatars = {
    default: 'https://avatars.mds.yandex.net/get-yapic/0/0-0/islands-middle',
    captain: 'https://avatars.mds.yandex.net/get-yapic/21377/enc-03e5d2c656b935040a0aae807a63eb82ab0efb114d01455b16146e2de4bc86f6/islands-retina-middle',
};
const previews = {
    zen: 'https://yastatic.net/s3/zen-lib/favicons4/favicon-32x32.png',
    q: 'https://yastatic.net/s3/home/services/all/svg/q0.svg',
    market: 'https://yastatic.net/s3/home/services/all/svg/market_2.svg',
    yandex: 'https://yastatic.net/s3/web4static/_/v2/ZcejnfbLE_TlMK13nS41mdC4A88.png',
    yandex2: 'https://yastatic.net/s3/home-static/_/37/37a02b5dc7a51abac55d8a5b6c865f0e.png',
    plus: 'https://avatars.mds.yandex.net/get-media-infra/3631343/7145dbb9-8add-43b5-829c-873cdaf89482/orig',
    afisha: 'https://yastatic.net/s3/home/services/block/afisha_new.svg',
    kinopoisk: 'https://yastatic.net/s3/home/services/block/kinopoisk_redesign0.svg',
};
service.zen = args => service({
    id: 'fakezen',
    name: 'Яндекс.Дзен',
    icon: previews.zen,
    ...args,
});
service.market = args => service({
    id: 'fakemarket',
    name: 'Яндекс.Маркет',
    icon: previews.market,
    ...args,
});
service.yandex = args => service({
    id: 'fakeservice',
    name: 'Яндекс',
    icon: previews.yandex,
    ...args,
});
service.q = args => service({
    id: 'fakeq',
    name: 'Кью',
    icon: previews.q,
    ...args,
});

const settings = settings => settings.reduce((a, s) => ({ ...a, ...s }), {});
const setting = ({
    text, enabled, name,
}) => ({
    [name]: {
        text, enabled,
    },
});

const notification = ({
    id,
    text,
    important,
    preview,
    groupID,
    mtime,
    is_read = false,
    is_new = true,
    avatar,
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
        actor: {
            avatar,
        },
        preview: {
            preview,
        },
    }),
    type: 'fake',
    mtime,
    is_read,
    is_new,
    important,
    groupID,
});
// Отсчет даты от 06.05.2022
const date = new Date();
date.setFullYear(2022);
date.setMonth(4);
date.setDate(6);
const dates = {
    // С шагом в пару минут
    recent: [...new Array(10)].map(
        (_, i) => new Date(new Date().setHours(12, i * 2, (23 * i) % 60, 0)).toISOString(),
    ),
    // Неделя - 16 дней в прошлое от 06.05.2022
    old: [...new Array(10)].map((_, i) => (
        new Date(new Date(date).setHours(12, i * 2, (23 * i) % 60, 0) - (7 + i) * 24 * 60 * 60 * 1000).toISOString()),
    ),
    // 0-9 месяцев в прошлое от 06.05.2022
    veryOld: [...new Array(10)].map((_, i) => (
        new Date(new Date(date).setHours(12, i * 2, (23 * i) % 60, 0) - (30 * i) * 24 * 60 * 60 * 1000).toISOString()),
    ),
};
const texts = {
    zen: [
        'Банк России увеличил долю золота и юаня в своих активах',
        'Куда вложить деньги на 3 месяца?',
        'Пост в сообществе: Цветущий мир',
        'Вот что у нас есть на тему Технологии и интернет',
        'Вот семь причин оформить кредитку Тинькофф Платинум вместо кредита',
    ],
    q: [
        'Илья Иноземцев добавил пост «3000! и конкурс»',
        'Мошенники перешли на VPN: ЦБ рассказал о новой схеме',
        'Виктория Смирнова: Собиратор юридических идей',
        'Сообщество для рекламодателей Яндекс Дзен',
        'Станьте экспертом Кью!',
    ],
    market: [
        'Заказ №123456789 уже спешит к вам. Курьер будет через 15 минут',
        'В корзине ждут 3 товара',
        'Ваш отзыв на «Губозакатывательная машинка» собрал 50 лайков',
        'Бесплатная доставка от 700 рублей',
        'Оставьте отзыв о товаре!',
    ],
    yandex: [
        'Алиса теперь умеет читать сказки',
        'OBI возобновит работу магазинов в России до конца майских праздников',
        'Курс доллара на сегодня: 72.71₽',
        'Афиша: Смотрите нового Бетмана сегодня вечером',
        'Плюс Мульти — экономия для всей семьи',
    ],
};
module.exports = {
    service, setting, settings, notification, req, dates, texts, previews, avatars,
};
