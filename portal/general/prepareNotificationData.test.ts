import { TMeta, getTexts } from './prepareNotificationData';

describe('getTexts', () => {
    const meta: TMeta = new Map([
        ['k1', { type: 'text', text: 't1' }],
        ['k2', { type: 'user', text: 't2', link: '//yandex.ru/' }],
        ['k3', { type: 'text', text: '' }],
    ]);

    it('Должен обработать текст', () => {
        expect(getTexts(meta, '')).toStrictEqual([]);
        expect(getTexts(meta, 'text')).toStrictEqual(['text']);
    });

    it('Должен обработать текст с одной переменной', () => {
        expect(getTexts(meta, '%{k1}')).toStrictEqual([
            { text: 't1' },
        ]);
        expect(getTexts(meta, '%{k2}text')).toStrictEqual([
            { text: 't2', link: '//yandex.ru/' },
            'text',
        ]);
        expect(getTexts(meta, 'text%{k1}')).toStrictEqual([
            'text',
            { text: 't1' },
        ]);
        expect(getTexts(meta, 'text%{k2}text')).toStrictEqual([
            'text',
            { text: 't2', link: '//yandex.ru/' },
            'text'
        ]);
    });

    it('Должен обработать текст с двумя переменными', () => {
        expect(getTexts(meta, '%{k1}%{k2}')).toStrictEqual([
            { text: 't1' },
            { text: 't2', link: '//yandex.ru/' },
        ]);

        expect(getTexts(meta, '%{k1}%{k2}text')).toStrictEqual([
            { text: 't1' },
            { text: 't2', link: '//yandex.ru/' },
            'text',
        ]);
        expect(getTexts(meta, 'text%{k1}%{k2}')).toStrictEqual([
            'text',
            { text: 't1' },
            { text: 't2', link: '//yandex.ru/' },
        ]);
        expect(getTexts(meta, '%{k1}text%{k2}')).toStrictEqual([
            { text: 't1' },
            'text',
            { text: 't2', link: '//yandex.ru/' },
        ]);

        expect(getTexts(meta, '%{k2}text%{k1}text')).toStrictEqual([
            { text: 't2', link: '//yandex.ru/' },
            'text',
            { text: 't1' },
            'text',
        ]);
        expect(getTexts(meta, 'text%{k2}text%{k1}')).toStrictEqual([
            'text',
            { text: 't2', link: '//yandex.ru/' },
            'text',
            { text: 't1' },
        ]);
        expect(getTexts(meta, 'text%{k2}%{k1}text')).toStrictEqual([
            'text',
            { text: 't2', link: '//yandex.ru/' },
            { text: 't1' },
            'text',
        ]);

        expect(getTexts(meta, 'text%{k1}text%{k2}text')).toStrictEqual([
            'text',
            { text: 't1' },
            'text',
            { text: 't2', link: '//yandex.ru/' },
            'text',
        ]);
    });

    it('Должен бросить ошибку', () => {
        expect(() => getTexts(meta, '%{k4}')).toThrowError('Invalid meta data');
        expect(() => getTexts(meta, '%{k3}')).toThrowError('Invalid meta text');
    });
});
