const TJSON = require('../tjson');

const TANKER_JSON = {
    keysets: {
        testkeyset1: {
            keys: {
                driver: {
                    info: {
                        context: '',
                        is_plural: true,
                        references: ''
                    },
                    translations: {
                        ru: {
                            status: 'approved',
                            form1: '%count% водитель',
                            form2: '%count% водителя',
                            form3: '%count% водителей'
                        },
                        en: {
                            status: 'approved',
                            form1: '%count% driver',
                            form2: '%count% drivers'
                        }
                    }
                },
                placeholderWithPercent: {
                    info: {
                        context: '',
                        is_plural: false,
                        references: ''
                    },
                    translations: {
                        ru: {
                            status: 'approved',
                            form: '%count%%'
                        },
                        en: {
                            status: 'approved',
                            form: '%count%%'
                        }
                    }
                },
                yandex: {
                    info: {
                        context: '',
                        is_plural: false,
                        references: ''
                    },
                    translations: {
                        ru: {
                            status: 'approved',
                            form: 'Яндекс'
                        },
                        en: {
                            status: 'approved',
                            form: 'Yandex'
                        }
                    }
                }
            },
            meta: {
                languages: ['ru', 'en']
            }
        },
        testkeyset2: {
            keys: {
                user: {
                    info: {
                        context: '',
                        is_plural: true,
                        references: ''
                    },
                    translations: {
                        ru: {
                            status: 'approved',
                            form1: '%count% пользователь',
                            form2: '%count% пользователя',
                            form3: '%count% пользователей'
                        }
                    }
                }
            },
            meta: {
                languages: ['ru']
            }
        },
        meta: {
            languages: ['ru']
        }
    }
};

describe('common utils: tjson', () => {
    describe('getInstance', () => {
        let tjson = new TJSON(TANKER_JSON);
        const i18n = tjson.getInstance('ru', 'testkeyset1');

        test('set возвращает объект с нужными полями', () => {
            expect(Object.keys(i18n)).toEqual(['print', 'getLang', 'getKeyset', 'keyset']);
        });

        test('getLang возвращает верный язык', () => {
            const i18nRu = tjson.getInstance('ru', 'testkeyset1');
            const i18nEn = tjson.getInstance('en', 'testkeyset1');

            expect(i18nRu.getLang()).toEqual('ru');
            expect(i18nEn.getLang()).toEqual('en');
        });

        test('getKeyset возвращает верный кейсет', () => {
            const i18nRu = tjson.getInstance('ru', 'testkeyset1');
            const i18nEn = tjson.getInstance('en', 'testkeyset2');

            expect(i18nRu.getKeyset()).toEqual('testkeyset1');
            expect(i18nEn.getKeyset()).toEqual('testkeyset2');
        });

        test('keyset создаёт новый инстанс с указаным кейсетом', () => {
            expect(i18n.getKeyset()).toEqual('testkeyset1');
            expect(i18n.keyset('testkeyset2').getKeyset()).toEqual('testkeyset2');

            // изначальный инстанс не подменился
            expect(i18n.getKeyset()).toEqual('testkeyset1');
            expect(i18n.print('yandex')).toEqual('Яндекс');
        });
    });

    describe('print', () => {
        let tjson = new TJSON(TANKER_JSON);
        const i18n = tjson.getInstance('ru', 'testkeyset1');

        test('print для простого ключа должен возвращать значение', () => {
            expect(i18n.print('yandex')).toBe('Яндекс');
        });

        test('print для множественного ключа должен возвращать значение учитывая count', () => {
            expect(i18n.print('driver', {count: 1})).toBe(
                TANKER_JSON.keysets.testkeyset1.keys.driver.translations.ru.form1
            );
            expect(i18n.print('driver', {count: 2})).toBe(
                TANKER_JSON.keysets.testkeyset1.keys.driver.translations.ru.form2
            );
            expect(i18n.print('driver', {count: 5})).toBe(
                TANKER_JSON.keysets.testkeyset1.keys.driver.translations.ru.form3
            );
            expect(i18n.print('driver')).toBe(TANKER_JSON.keysets.testkeyset1.keys.driver.translations.ru.form3);
        });

        test('print c placeholder - реплейсит значение', () => {
            expect(
                i18n.print('driver', {
                    count: 1,
                    placeholder: {count: 1}
                })
            ).toBe(TANKER_JSON.keysets.testkeyset1.keys.driver.translations.ru.form1.replace('%count%', 1));
            expect(i18n.print('placeholderWithPercent', {
                placeholder: {
                    count: 10
                }
            })).toBe('10%');
        });
    });

    describe('import', () => {
        test('import заполняет кейсет', () => {
            let tjson = new TJSON();
            const i18n = tjson.getInstance('ru', 'testkeyset');

            expect(i18n.print('test')).toBe(undefined);

            tjson.import({testkeyset: {test: {form: 'Тест'}}}, 'ru');

            expect(i18n.print('test')).toBe('Тест');
        });
    });

    describe('export', () => {
        test('export возвращает tjson', () => {
            let tjson = new TJSON(TANKER_JSON);

            expect(tjson.export('en').testkeyset1).toBeDefined();
            expect(tjson.export('en').testkeyset2).toBeUndefined();
        });
    });
});
