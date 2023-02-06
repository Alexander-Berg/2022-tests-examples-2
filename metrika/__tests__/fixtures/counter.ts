import { CounterFullData } from 'server/api/types/counter';

/* yaspeller ignore:start */
export const counter: Partial<CounterFullData> = {
    id: 101024,
    status: 'Active',
    ownerLogin: 'sendflowers-amf',
    codeStatus: 'CS_OK',
    name: 'AMF - международная сеть доставки цветов',
    site: 'sendflowers.ru',
    type: 'simple',
    favorite: 0,
    features: [],
    goals: [
        {
            id: 2899978,
            name: 'Вход в корзину',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            flag: 'basket',
            conditions: [
                {
                    type: 'exact',
                    url: 'www.sendflowers.ru/cart.phtml',
                },
            ],
            class: 1,
        },
        {
            id: 3290299,
            name: 'Оформление интерьеров',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'http://www.sendflowers.ru/rus/info/2009.html',
                },
            ],
            class: 0,
        },
        {
            id: 4105168,
            name: '8 марта 2014. 101 тюльпан',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: '080314BASKET101',
                },
            ],
            class: 0,
        },
        {
            id: 4105171,
            name: '8 марта 2014. 51 тюльпан',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: '080314BASKET51',
                },
            ],
            class: 0,
        },
        {
            id: 4105174,
            name: '8 марта 2014. Заказали обратный звонок',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: '080314CALLME',
                },
            ],
            class: 1,
        },
        {
            id: 5133665,
            name: 'корзина воронка',
            type: 'step',
            isRetargeting: 0,
            steps: [
                {
                    id: 5133668,
                    name: 'корзина',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 0,
                    conditions: [
                        {
                            type: 'contain',
                            url: 'cart.phtml',
                        },
                    ],
                    class: 1,
                },
                {
                    id: 5133671,
                    name: 'адрес',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 5133668,
                    conditions: [
                        {
                            type: 'contain',
                            url: 'shipping/',
                        },
                    ],
                    class: 1,
                },
                {
                    id: 5133674,
                    name: 'оплата',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 5133671,
                    conditions: [
                        {
                            type: 'contain',
                            url: '/cart/payment/',
                        },
                    ],
                    class: 1,
                },
                {
                    id: 5133677,
                    name: 'подтверждение заказа',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 5133674,
                    conditions: [
                        {
                            type: 'contain',
                            url: '/cart/confirm/',
                        },
                    ],
                    class: 1,
                },
                {
                    id: 5133680,
                    name: 'оплата',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 5133677,
                    conditions: [
                        {
                            type: 'contain',
                            url: '/completed',
                        },
                    ],
                    class: 1,
                },
            ],
            class: 1,
        },
        {
            id: 5232020,
            name: 'Обратный звонок',
            type: 'step',
            isRetargeting: 0,
            steps: [
                {
                    id: 5232023,
                    name: 'Заказать об.зв.',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 0,
                    conditions: [
                        {
                            type: 'action',
                            url: 'ORDER1',
                        },
                    ],
                    class: 0,
                },
                {
                    id: 5232026,
                    name: 'отправили',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 5232023,
                    conditions: [
                        {
                            type: 'action',
                            url: 'ORDER2',
                        },
                    ],
                    class: 0,
                },
            ],
            class: 0,
        },
        {
            id: 6799211,
            name: 'Новый год',
            type: 'url',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: 'new_year',
                },
            ],
            class: 0,
        },
        {
            id: 5231966,
            name: 'Оформление интерьеров',
            type: 'step',
            isRetargeting: 0,
            steps: [
                {
                    id: 5231969,
                    name: 'отправить заявку',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 0,
                    conditions: [
                        {
                            type: 'action',
                            url: 'ORDER5',
                        },
                    ],
                    class: 0,
                },
                {
                    id: 5231972,
                    name: 'отправили',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 5231969,
                    conditions: [
                        {
                            type: 'action',
                            url: 'ORDER6',
                        },
                    ],
                    class: 0,
                },
            ],
            class: 0,
        },
        {
            id: 5231948,
            name: 'Быстрый заказ',
            type: 'step',
            isRetargeting: 0,
            steps: [
                {
                    id: 5231951,
                    name: 'Быстрый заказ',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 0,
                    conditions: [
                        {
                            type: 'action',
                            url: 'ORDER3',
                        },
                    ],
                    class: 0,
                },
                {
                    id: 5231954,
                    name: 'Оформить заказ',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 5231951,
                    conditions: [
                        {
                            type: 'action',
                            url: 'ORDER4',
                        },
                    ],
                    class: 0,
                },
            ],
            class: 0,
        },
        {
            id: 3290296,
            name: 'Оформление к Новому году',
            type: 'url',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'http://www.sendflowers.ru/rus/info/1604.html',
                },
            ],
            class: 0,
        },
        {
            id: 3176764,
            name: 'Свадьба',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: 'wedding',
                },
            ],
            class: 1,
        },
        {
            id: 2899981,
            name: 'Покупка - оплата наличными курьеру',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            flag: 'order',
            conditions: [
                {
                    type: 'contain',
                    url: 'AMFset[CustomerOrderNumber]',
                },
            ],
            class: 1,
        },
        {
            id: 3176497,
            name: 'Все посетители',
            type: 'number',
            isRetargeting: 1,
            depth: 2,
            class: 0,
        },
        {
            id: 3176500,
            name: 'Просмотр 3 страниц сайта',
            type: 'number',
            isRetargeting: 1,
            depth: 3,
            class: 1,
        },
        {
            id: 5231957,
            name: 'Свадьба',
            type: 'step',
            isRetargeting: 0,
            steps: [
                {
                    id: 5231960,
                    name: 'Отправить заявку',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 0,
                    conditions: [
                        {
                            type: 'action',
                            url: 'ORDER7',
                        },
                    ],
                    class: 0,
                },
                {
                    id: 5231963,
                    name: 'Отправили',
                    type: 'url',
                    isRetargeting: 0,
                    prevGoalId: 5231960,
                    conditions: [
                        {
                            type: 'action',
                            url: 'ORDER8',
                        },
                    ],
                    class: 0,
                },
            ],
            class: 0,
        },
        {
            id: 3176503,
            name: 'Посетили корзину',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: '/cart',
                },
            ],
            class: 1,
        },
        {
            id: 3176557,
            name: 'Интересовались букетами',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: 'bouquets',
                },
            ],
            class: 0,
        },
        {
            id: 3176575,
            name: 'Интересовались композициями',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: 'arrangement',
                },
            ],
            class: 0,
        },
        {
            id: 3176578,
            name: 'Интересовались корзинами',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: 'baskets',
                },
            ],
            class: 0,
        },
        {
            id: 3176581,
            name: 'Интересовались подарками',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: 'presents',
                },
            ],
            class: 0,
        },
        {
            id: 7526146,
            name: '14 февраля',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: 'february',
                },
            ],
            class: 1,
        },
        {
            id: 7989291,
            name: '8 марта',
            type: 'url',
            isRetargeting: 1,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: 'march',
                },
            ],
            class: 1,
        },
        {
            id: 13846275,
            name: 'нет изображений',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'NOIMAGE',
                },
            ],
            class: 1,
        },
        {
            id: 13860200,
            name: 'Ошибка 404',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'ERROR404',
                },
            ],
            class: 0,
        },
        {
            id: 13860205,
            name: 'Ошибка 500',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'ERROR500',
                },
            ],
            class: 0,
        },
        {
            id: 13860210,
            name: 'Ошибка неизвестна',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'ERRORUNKNOWN',
                },
            ],
            class: 0,
        },
        {
            id: 17202110,
            name: 'Переход на страницу контактов',
            type: 'url',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: '/rus/firmennye-salony/',
                },
            ],
            class: 0,
        },
        {
            id: 17202210,
            name: 'Переход на страницу "О компании"',
            type: 'url',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: '/rus/info/kompaniya/',
                },
            ],
            class: 0,
        },
        {
            id: 17202215,
            name: 'Переход на страницу "Скидки"',
            type: 'url',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: '/rus/skidki/',
                },
            ],
            class: 0,
        },
        {
            id: 17202220,
            name: 'Переход на страницу "Гарантия качества"',
            type: 'url',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: '/rus/kachestvo/',
                },
            ],
            class: 0,
        },
        {
            id: 17202225,
            name: 'Переход на страницу "Напомнить о дате"',
            type: 'url',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: '/rus/info/napominanie/',
                },
            ],
            class: 0,
        },
        {
            id: 17202230,
            name: 'Переход на страницу отзывов',
            type: 'url',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: '/rus/info/1013.html',
                },
            ],
            class: 0,
        },
        {
            id: 17202235,
            name: 'Отправка отзыва или жалобы',
            type: 'url',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'contain',
                    url: '/rus/info/90.html',
                },
            ],
            class: 0,
        },
        {
            id: 17500490,
            name: 'SEO. Подписка на новости',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'SUBSCRIBE_NEWS',
                },
            ],
            class: 0,
        },
        {
            id: 17501485,
            name: 'SEO. Быстрый заказ',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'FAST_ORDER',
                },
            ],
            class: 0,
        },
        {
            id: 17501490,
            name: 'SEO. Форма похвалить',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'FORM_COMPLIMENT',
                },
            ],
            class: 0,
        },
        {
            id: 17501495,
            name: 'SEO. Форма пожаловаться',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'FORM_COMPLAIN',
                },
            ],
            class: 0,
        },
        {
            id: 17501600,
            name: 'SEO. Рекомендации в корзине',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'RECOMMENDATION_BASKET',
                },
            ],
            class: 0,
        },
        {
            id: 17501605,
            name: 'SEO. Рекомендации на карточке товара',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'RECOMMENDATION_ARTICLE',
                },
            ],
            class: 0,
        },
        {
            id: 17644590,
            name: 'Нажата "Наверх"',
            type: 'action',
            isRetargeting: 0,
            prevGoalId: 0,
            conditions: [
                {
                    type: 'exact',
                    url: 'CLICK_GO_TOP',
                },
            ],
            class: 0,
        },
    ],
    createTime: '2008-08-25T16:49:51+03:00',
    partnerId: 0,
    updateTime: '2015-08-19 11:18:43',
    filterRobots: 1,
    timeZoneName: 'Europe/Moscow',
    timeZoneOffset: 180,
    visitThreshold: 1800,
    maxGoals: 200,
    maxOperations: 30,
    maxFilters: 30,
} as Partial<CounterFullData>;
/* yaspeller ignore:end */
