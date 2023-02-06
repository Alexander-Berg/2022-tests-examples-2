import zoneInfo from '../zoneInfo';

const tariffsWithDefault = [
    {id: 'start', can_be_default: true},
    {id: 'econom', is_default: true},
    {id: 'night', can_be_default: true}
];

const tariffsWithCanBeDefault = [
    {id: 'econom'},
    {id: 'night', can_be_default: true},
    {id: 'uberx', can_be_default: true}
];

const tariffsWithoutDefault = [{id: 'econom'}, {id: 'night'}, {id: 'uberx'}];

describe('zoneInfo', () => {
    describe('getDefaultTariff', () => {
        it('Должен вернуть дефолтный при отстутсвии выбранного', () => {
            expect(zoneInfo.getDefaultTariff(undefined, tariffsWithDefault)).toBe(tariffsWithDefault[1]);
        });
        it('Должен вернуть первый доступный для дефолта при отстутсвии выбранного', () => {
            expect(zoneInfo.getDefaultTariff(undefined, tariffsWithCanBeDefault)).toBe(tariffsWithCanBeDefault[1]);
        });
        it('Должен вернуть первый при отстутсвии выбранного', () => {
            expect(zoneInfo.getDefaultTariff(undefined, tariffsWithoutDefault)).toBe(tariffsWithoutDefault[0]);
        });

        it('Должен вернуть выбранный ранее при его наличии', () => {
            expect(zoneInfo.getDefaultTariff('start', tariffsWithDefault)).toBe(tariffsWithDefault[0]);
        });

        it('Должен вернуть дефолт если выбранного ранее нет', () => {
            expect(zoneInfo.getDefaultTariff('test', tariffsWithDefault)).toBe(tariffsWithDefault[1]);
        });
    });

    describe('getRequirements', () => {
        const tariff = {
            class: 'econom',
            id: 'econom',
            name: 'Эконом',
            supported_requirements: [
                {
                    default: false,
                    label: 'Жёлтые номера',
                    name: 'yellowcarnumber',
                    persistent: false,
                    required: false,
                    tariff_specific: false,
                    type: 'boolean'
                },
                {
                    default: false,
                    driver_name: '"><img src=x onerror=alert(\'XSS\')>',
                    label: 'Некурящий водитель',
                    name: 'nosmoking',
                    persistent: true,
                    type: 'boolean'
                },
                {
                    default: 0,
                    description: 'Вы можете выбрать кресло или бустер.',
                    driver_name: 'childchair',
                    label: 'Детское кресло',
                    max_weight: 3.0,
                    multiselect: true,
                    name: 'childchair_moscow',
                    persistent: false,
                    required: false,
                    select: {
                        caption: 'Выберите тип сиденья:',
                        options: [
                            {
                                independent_tariffication: true,
                                label: '9-18 кг, от 9 месяцев до 4 лет',
                                max_count: 1,
                                name: 'infant',
                                style: 'spinner',
                                title: 'Малыш до 4 лет',
                                value: 1,
                                weight: 2.0
                            },
                            {
                                independent_tariffication: true,
                                label: '15-25 кг, от 3 до 7 лет',
                                max_count: 1,
                                name: 'chair',
                                style: 'spinner',
                                title: 'Ребёнок 3–7 лет',
                                value: 3,
                                weight: 2.0
                            },
                            {
                                independent_tariffication: true,
                                label: '22-36 кг, от 7 до 12 лет',
                                max_count: 1,
                                name: 'booster',
                                style: 'spinner',
                                title: 'Бустер',
                                title_forms: {
                                    '1': 'Бустер'
                                },
                                value: 7,
                                weight: 2.0
                            }
                        ],
                        type: 'number'
                    },
                    tariff_specific: false,
                    type: 'select'
                },
                {
                    default: false,
                    driver_name: 'conditioner',
                    label: 'Кондиционер',
                    name: 'conditioner',
                    persistent: false,
                    type: 'boolean'
                },
                {
                    default: 0,
                    driver_name: 'count_luggage',
                    label: 'Кол-во багажа',
                    multiselect: false,
                    name: 'count_luggage',
                    persistent: false,
                    required: false,
                    select: {
                        caption: 'Кол-во багажа',
                        options: [
                            {
                                independent_tariffication: true,
                                label: 'Чемодан',
                                max_count: 1,
                                name: 'suitcase',
                                title: 'Чемодан',
                                value: 1
                            },
                            {
                                independent_tariffication: true,
                                label: 'Два чемодана',
                                name: 'suitcase2',
                                title: 'Два чемодана',
                                value: 2
                            },
                            {
                                independent_tariffication: true,
                                label: 'Три чемодана',
                                name: 'suitcase3',
                                title: 'Три чемодана',
                                value: 3
                            }
                        ],
                        type: 'number'
                    },
                    tariff_specific: false,
                    type: 'select'
                },
                {
                    default: false,
                    driver_name: 'bicycle',
                    label: 'Велосипед',
                    name: 'bicycle',
                    persistent: false,
                    redirect: {
                        description: 'Доступно в тарифе «Минивэн»',
                        requirement_name: 'bicycle',
                        tariff_class: 'minivan'
                    },
                    type: 'boolean'
                }
            ]
        };

        it('Должен вернуть пустые требования, если ничего не выберали', () => {
            expect(zoneInfo.getRequirements(tariff, {})).toEqual({});
        });
        it('Должен игнорировать неподдерживаемые требования в тарифе', () => {
            expect(
                zoneInfo.getRequirements(tariff, {
                    test: true,
                    old: true,
                    test2: [7]
                })
            ).toEqual({});
        });
        it('Должен вернуть только входящие в тариф требования', () => {
            expect(
                zoneInfo.getRequirements(tariff, {
                    test: true,
                    nosmoking: true,
                    childchair_moscow: [7],
                    count_luggage: 2
                })
            ).toEqual({nosmoking: true, childchair_moscow: [7], count_luggage: 2});
        });
        it('Должен игнорировать требования с redirect', () => {
            expect(
                zoneInfo.getRequirements(tariff, {
                    bicycle: true
                })
            ).toEqual({});
        });
        it('Должен игнорировать неподдерживаемые значения', () => {
            expect(
                zoneInfo.getRequirements(tariff, {
                    count_luggage: 100,
                    childchair_moscow: [100]
                })
            ).toEqual({});
        });
        it('Должен установить только поддерживаемые значения', () => {
            expect(
                zoneInfo.getRequirements(tariff, {
                    count_luggage: 2,
                    childchair_moscow: [1, 3, 100]
                })
            ).toEqual({
                count_luggage: 2,
                childchair_moscow: [1, 3]
            });
        });
    });
});
