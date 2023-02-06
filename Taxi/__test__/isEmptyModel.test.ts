import {isEmptyModel} from '../isEmptyModel';

describe('isEmptyModel', () => {
    it('Модель пустая', () => {
        const MODELS = [
            undefined,
            {},
            {
                name: undefined,
            },
            {
                name: '',
            },
            {
                fields: {},
                colors: [],
            },
        ];

        expect(MODELS.every(isEmptyModel)).toBeTruthy();
    });

    it('Модель не пустая', () => {
        const MODELS = [
            {
                age: 0,
            },
            {
                name: '0',
            },
            {
                colors: [undefined],
            },
        ];

        expect(MODELS.every(model => !isEmptyModel(model))).toBeTruthy();
    });
});
