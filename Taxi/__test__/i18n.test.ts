import TJSON from '../localization/tjson';

const keysets = {
    common: {
        keys: {
            paramOnly: {
                info: {is_plural: false},
                translations: {ru: {form: '%param1%'}}
            },
            percentFirst: {
                info: {is_plural: false},
                translations: {ru: {form: '%%param1%'}}
            },
            percentInTheMiddle: {
                info: {is_plural: false},
                translations: {ru: {form: '%param1%% % str %% %param2% str'}}
            },
            percentLast: {
                info: {is_plural: false},
                translations: {ru: {form: '%param1%%'}}
            }
        },
        meta: {languages: ['ru'], context: ''}
    }
};

const i18n = new TJSON({keysets}).lang('ru').keyset('common');

describe('i18n.print', () => {
    test('Параметр корректно заменяется', () => {
        const param1 = 'text';
        const text = i18n.print('paramOnly', {
            placeholder: {
                param1
            }
        });

        expect(text).toBe(param1);
    });

    test('Знак процента корректно обрабатывается в начале', () => {
        const param1 = 'text';
        const text = i18n.print('percentFirst', {
            placeholder: {
                param1
            }
        });

        expect(text).toBe(`%${param1}`);
    });

    test('Знак процента корректно обрабатывается в середине', () => {
        const param1 = 'text';
        const param2 = 'text2';
        const text = i18n.print('percentInTheMiddle', {
            placeholder: {
                param1,
                param2
            }
        });

        expect(text).toBe(`${param1}% % str %% ${param2} str`);
    });

    test('Знак процента корректно обрабатывается в конце', () => {
        const param1 = 'text';
        const text = i18n.print('percentLast', {
            placeholder: {
                param1
            }
        });

        expect(text).toBe(`${param1}%`);
    });
});
