import {DiscountInformer, InformerMeta} from '../../../../types';
import {prepareModelToInformer} from '../informer';

describe('prepareModelToInformer', () => {
    it('Все поля информера заполнены', () => {
        const MODEL: InformerMeta = {
            text: 'текст информера',
            picture: 'картинка информера',
            color: 'F0F0F0',
            modal: {
                header: 'заголовок модалки',
                text: 'текст модалки',
                picture: 'картинка модалки',
                firstButton: {
                    text: 'текст первой кнопки',
                    link: 'ссылка первой кнопки',
                    color: 'A9A9A9',
                },
                secondButton: {
                    text: 'текст второй кнопки',
                    link: 'ссылка второй кнопки',
                    color: 'FEFEFE',
                },
            },
        };

        const RESULT: DiscountInformer = {
            text: 'текст информера',
            picture: 'картинка информера',
            color: '#F0F0F0',
            modal: {
                title: 'заголовок модалки',
                text: 'текст модалки',
                picture: 'картинка модалки',
                buttons: [
                    {
                        text: 'текст первой кнопки',
                        color: '#A9A9A9',
                        uri: 'ссылка первой кнопки',
                    },
                    {
                        text: 'текст второй кнопки',
                        color: '#FEFEFE',
                        uri: 'ссылка второй кнопки',
                    },
                ],
            },
        };

        expect(prepareModelToInformer(MODEL)).toEqual(RESULT);
    });

    it('Заполнена только одна кнопка', () => {
        const MODEL: InformerMeta = {
            text: 'текст информера',
            picture: 'картинка информера',
            color: 'F0F0F0',
            modal: {
                header: 'заголовок модалки',
                text: 'текст модалки',
                picture: 'картинка модалки',
                firstButton: {
                    text: 'текст первой кнопки',
                    link: 'ссылка первой кнопки',
                    color: 'A9A9A9',
                },
                secondButton: {
                    text: '',
                    link: '',
                    color: '',
                },
            },
        };

        const RESULT: DiscountInformer = {
            text: 'текст информера',
            picture: 'картинка информера',
            color: '#F0F0F0',
            modal: {
                title: 'заголовок модалки',
                text: 'текст модалки',
                picture: 'картинка модалки',
                buttons: [
                    {
                        text: 'текст первой кнопки',
                        color: '#A9A9A9',
                        uri: 'ссылка первой кнопки',
                    },
                ],
            },
        };

        expect(prepareModelToInformer(MODEL)).toEqual(RESULT);
    });

    it('Не обязательные поля не заполнены, но в модалке есть кнопки заполненные только обязательными полями', () => {
        const MODEL: InformerMeta = {
            text: 'текст информера',
            picture: 'картинка информера',
            color: 'F0F0F0',
            modal: {
                header: '',
                text: '',
                picture: '',
                firstButton: {
                    text: 'текст первой кнопки',
                    link: '',
                    color: 'A9A9A9',
                },
                secondButton: {
                    text: 'текст второй кнопки',
                    link: '',
                    color: 'FEFEFE',
                },
            },
        };

        const RESULT: DiscountInformer = {
            text: 'текст информера',
            picture: 'картинка информера',
            color: '#F0F0F0',
            modal: {
                buttons: [
                    {
                        text: 'текст первой кнопки',
                        color: '#A9A9A9',
                    },
                    {
                        text: 'текст второй кнопки',
                        color: '#FEFEFE',
                    },
                ],
            },
        };

        expect(prepareModelToInformer(MODEL)).toEqual(RESULT);
    });

    it('Заполнен только модалка, информер не заполнен', () => {
        const MODEL: InformerMeta = {
            text: 'текст информера',
            picture: 'картинка информера',
            color: 'F0F0F0',
            modal: {
                header: '',
                text: '',
                picture: '',
                firstButton: {
                    text: '',
                    link: '',
                    color: '',
                },
                secondButton: {
                    text: '',
                    link: '',
                    color: '',
                },
            },
        };

        const RESULT: DiscountInformer = {
            text: 'текст информера',
            picture: 'картинка информера',
            color: '#F0F0F0',
        };

        expect(prepareModelToInformer(MODEL)).toEqual(RESULT);
    });

    it('Поля информера не заполнены', () => {
        const MODEL: InformerMeta = {
            text: '',
            picture: '',
            color: '',
            modal: {
                header: '',
                text: '',
                picture: '',
                firstButton: {
                    text: '',
                    link: '',
                    color: '',
                },
                secondButton: {
                    text: '',
                    link: '',
                    color: '',
                },
            },
        };

        expect(prepareModelToInformer(MODEL)).toBeUndefined();
    });
});
