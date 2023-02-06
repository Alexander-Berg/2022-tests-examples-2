import putCustomsFieldsInStore from '../putCustomsFieldsInStore';

describe('passport/routes/common/putCustomsFieldsInStore', () => {
    it('should add configs from enviroments', () => {
        const originNodeEnv = process.env.NODE_ENV;

        process.env.NODE_ENV = 'development';

        const originalConfig = {
            environments: {
                development: {
                    autoRuButton: {
                        link: 'https://auth.test.avto.ru'
                    }
                }
            }
        };
        const store = {};
        const isNeoPhonishRegisterAvailable = false;
        const flags = [];
        const lang = 'ru';

        putCustomsFieldsInStore(originalConfig, store, isNeoPhonishRegisterAvailable, flags, lang);

        expect(store.customs.autoRuButton).toEqual({link: 'https://auth.test.avto.ru'});

        process.env.NODE_ENV = originNodeEnv;
    });
});
