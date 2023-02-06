const {helpers} = require('../docCenter');

describe('docCenter api helpers', () => {
    describe('flattenMenu', () => {
        let tree = [
            {
                title: 'Мобильное приложение',
                id: 'taxi-app/index.html'
            },
            {
                title: 'Проблема с поездкой',
                id: 'taxi-app/solve-problems.html',
                content: [
                    {
                        title: 'Неправильная стоимость',
                        id: 'taxi-app/feedback/questions-cost-trip.html'
                    },
                    {
                        title: 'Проблема с оплатой',
                        id: 'taxi-app/problem-pay.html',
                        content: [
                            {
                                title: 'Оплатил поездку дважды',
                                id: 'taxi-app/feedback/double-pay.html'
                            },
                            {
                                title: 'У водителя не было сдачи',
                                id: 'taxi-app/feedback/no-change.html',
                                hidden: 'yes'
                            },
                            {
                                title: 'Нет денег на карте',
                                id: 'taxi-app/feedback/no-money.html',
                                content: [
                                    {
                                        title: 'Нехватило денег для списание',
                                        id: 'taxi-app/feedback/limit-pay.html'
                                    },
                                    {
                                        title: 'На счету отрицительный баланс',
                                        id: 'taxi-app/feedback/minus-balance.html'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        title: 'Проблема с подачей такси',
                        id: 'taxi-app/feedback/feeding.html'
                    }
                ]
            },
            {
                hidden: 'yes',
                title: 'Яндекс.Такси и данные пользователя',
                id: 'taxi-app/data-collection.html'
            }
        ];

        test('Должен разложить дерево в плоский список содержаний контент и скрыть невидиммые', () => {
            const actual = helpers.flattenMenu(tree, {});
            expect(actual).toEqual({
                'taxi-app/feedback/no-money.html': {
                    content: [
                        {id: 'taxi-app/feedback/limit-pay.html', title: 'Нехватило денег для списание'},
                        {id: 'taxi-app/feedback/minus-balance.html', title: 'На счету отрицительный баланс'}
                    ],
                    id: 'taxi-app/feedback/no-money.html',
                    title: 'Нет денег на карте'
                },
                'taxi-app/problem-pay.html': {
                    content: [
                        {id: 'taxi-app/feedback/double-pay.html', title: 'Оплатил поездку дважды'},
                        {id: 'taxi-app/feedback/no-money.html', title: 'Нет денег на карте'}
                    ],
                    id: 'taxi-app/problem-pay.html',
                    title: 'Проблема с оплатой'
                },
                'taxi-app/solve-problems.html': {
                    content: [
                        {id: 'taxi-app/feedback/questions-cost-trip.html', title: 'Неправильная стоимость'},
                        {id: 'taxi-app/problem-pay.html', title: 'Проблема с оплатой'},
                        {id: 'taxi-app/feedback/feeding.html', title: 'Проблема с подачей такси'}
                    ],
                    id: 'taxi-app/solve-problems.html',
                    title: 'Проблема с поездкой'
                }
            });
        });
    });

    describe('normalizeTree', () => {
        let originTree;

        beforeEach(() => {
            originTree = [
                {
                    item: {
                        title: 'Неправильная стоимость',
                        path: 'taxi-app/feedback/questions-cost-trip.html',
                        normalizedPath: 'taxi-app/feedback/questions-cost-trip.html'
                    }
                },
                {
                    item: {
                        title: 'Проблема с оплатой',
                        path: 'taxi-app/problem-pay.html',
                        content: [
                            {
                                item: {
                                    title: 'Оплатил поездку дважды',
                                    path: 'taxi-app/feedback/double-pay.html',
                                    normalizedPath: 'taxi-app/feedback/double-pay.html'
                                }
                            },
                            {
                                item: {
                                    title: 'У водителя не было сдачи',
                                    path: 'taxi-app/feedback/no-change.html',
                                    normalizedPath: 'taxi-app/feedback/no-change.html'
                                }
                            }
                        ],
                        normalizedPath: 'taxi-app/problem-pay.html'
                    }
                }
            ];
        });

        test('Преобразует входное дерево в упрощенный вид', () => {
            expect(helpers.normalizeTree(originTree, {root: '/help'})).toEqual([
                {
                    id: '/taxi-app/feedback/questions-cost-trip.html',
                    path: '/taxi-app/feedback/questions-cost-trip.html',
                    title: 'Неправильная стоимость'
                },
                {
                    content: [
                        {
                            id: '/taxi-app/feedback/double-pay.html',
                            path: '/taxi-app/feedback/double-pay.html',
                            title: 'Оплатил поездку дважды'
                        },
                        {
                            id: '/taxi-app/feedback/no-change.html',
                            path: '/taxi-app/feedback/no-change.html',
                            title: 'У водителя не было сдачи'
                        }
                    ],
                    id: '/taxi-app/problem-pay.html',
                    path: '/taxi-app/problem-pay.html',
                    title: 'Проблема с оплатой'
                }
            ]);
        });
    });

    describe('buildFormQuery', () => {
        test('Должен преобразовать опции в id полей формы', () => {
            const options = {
                phone: '+700',
                pageId: 'test.html',
                orderid: 123
            };

            const forms = {
                4730: {
                    // прод форма
                    answer_1: 'phone',
                    answer_2: 'pageId',
                    OrderId: 'orderid'
                }
            };

            expect(helpers.buildFormQuery(forms, options)).toEqual({
                'form-answer_1': options.phone,
                'form-answer_2': options.pageId,
                'form-OrderId': options.orderid
            });
        });

        test('Должен вернуть пустой объект, если поля не сматчились', () => {
            const options = {
                nophone: '+700',
                nopageId: 'test.html',
                noorderid: 123
            };

            expect(helpers.buildFormQuery(options)).toEqual({});
        });

        test('Должен вернуть пустой объект, если опции пустые', () => {
            expect(helpers.buildFormQuery()).toEqual({});
            expect(helpers.buildFormQuery('')).toEqual({});
            expect(helpers.buildFormQuery({})).toEqual({});
        });
    });

    describe('buildTemplateQuery', () => {
        test('Должен преобразовать опции в template поля', () => {
            const options = {
                phone: '+7919',
                countryId: 'KZ'
            };

            const fields = {
                phone: 'phone',
                countryId: 'country'
            };

            expect(helpers.buildTemplateQuery(fields, options)).toEqual({
                'template-phone': '+7919',
                'template-country': 'kz'
            });
        });

        test('Должен вернуть пустой объект, если поля не сматчились', () => {
            const options = {
                nophone: '+700',
                nopageId: 'test.html',
                noorderid: 123
            };

            expect(helpers.buildTemplateQuery(options)).toEqual({});
        });

        test('Должен вернуть пустой объект, если опции пустые', () => {
            expect(helpers.buildTemplateQuery()).toEqual({});
            expect(helpers.buildTemplateQuery('')).toEqual({});
            expect(helpers.buildTemplateQuery({})).toEqual({});
        });
    });

    describe('stringifyComponents', () => {
        it('Должен вернуть undefined, если нет компонентов', () => {
            expect(helpers.stringifyComponents()).toEqual(undefined);
            expect(helpers.stringifyComponents({})).toEqual(undefined);
        });

        it('Компонент без аргументов', () => {
            expect(helpers.stringifyComponents({menu: true})).toEqual('menu()');
        });

        it('Компонент c аргументами', () => {
            expect(
                helpers.stringifyComponents({
                    menu: {
                        json: true
                    }
                })
            ).toEqual('menu(json=true)');
        });

        it('Правильный разделитель между компонентами', () => {
            expect(helpers.stringifyComponents({menu: true, content: true})).toEqual('content(),menu()');
        });

        it('Правильный разделитель между аргументами', () => {
            expect(
                helpers.stringifyComponents({
                    menu: {
                        json: true,
                        param2: false
                    }
                })
            ).toEqual('menu(json=true|param2=false)');
        });
    });
});
