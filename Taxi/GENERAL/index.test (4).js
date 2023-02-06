const {inheritNode, getMeta, getBunkerCountries} = require('./index');

describe('middleware v2 utils', () => {
    describe('inheritNode', () => {
        const bunker = {
            country: {
                int: {
                    a: 1,
                    b: {
                        b: 2
                    },
                    c: 3
                },
                ru: {
                    a: '1',
                    inherit: 'int'
                },
                kz: {
                    c: 4,
                    inherit: 'ru',
                    b: {
                        c: 3,
                        inherit: 'int.b'
                    }
                }
            }
        };

        it('Если в объекте нет признака наследования, возвращает исходные данные', () => {
            expect(inheritNode(bunker, 'country', bunker.country.int)).toEqual({
                a: 1,
                b: {
                    b: 2
                },
                c: 3
            });
        });

        it('Должен отнаследовать данные от родителей', () => {
            expect(inheritNode(bunker, 'country', bunker.country.ru)).toEqual({
                a: '1',
                b: {
                    b: 2
                },
                c: 3
            });
        });

        it('Должен отнаследовать данные от родителей включая дочерние элементы', () => {
            expect(inheritNode(bunker, 'country', bunker.country.kz)).toEqual({
                a: '1',
                b: {
                    b: 2,
                    c: 3
                },
                c: 4
            });
        });
    });

    describe('getMeta', () => {
        const bunker = {
            defaultCountry: 'int',
            ru: {
                languages: ['ru'],
                pages: {test: {}}
            },
            int: {
                languages: ['ru', 'en', 'fi'],
                pages: {test: {}}
            }
        };

        it('Возвращает meta данные с указанием дефолта', () => {
            expect(getMeta('test', bunker)).toEqual({
                ru: {
                    domain: null,
                    isDefaultForDomain: false,
                    isDefault: false,
                    languages: ['ru']
                },
                int: {
                    domain: null,
                    isDefaultForDomain: false,
                    isDefault: true,
                    languages: ['ru', 'en', 'fi']
                }
            });
        });

        it('Возвращает meta данные с учетом доменов', () => {
            expect(
                getMeta('test', {
                    countriesByDomain: {
                        ru: ['ru'],
                        com: ['int', 'ru']
                    },
                    ...bunker
                })
            ).toEqual({
                ru: {
                    domain: 'ru',
                    isDefaultForDomain: true,
                    isDefault: false,
                    languages: ['ru']
                },
                int: {
                    domain: 'com',
                    isDefaultForDomain: true,
                    isDefault: true,
                    languages: ['ru', 'en', 'fi']
                }
            });
        });
    });

    describe('getBunkerCountries', () => {
        it('Возвращает meta данные с учетом доменов', () => {
            expect(
                getBunkerCountries({
                    defaultCountry: 'int',
                    userAutodetect: true,
                    fixedRegion: 'ru_int',
                    defaultDomain: 'ru',
                    ru: {
                        languages: ['ru'],
                        defaultLang: 'ru'
                    },
                    int: {
                        languages: ['ru', 'en'],
                        defaultLang: 'en'
                    }
                })
            ).toEqual({
                int: {
                    defaultLang: 'en',
                    languages: ['ru', 'en']
                },
                ru: {
                    defaultLang: 'ru',
                    languages: ['ru']
                }
            });
        });
    });
});
