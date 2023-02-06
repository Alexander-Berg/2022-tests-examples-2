import defineLanguage from '../defineLanguage';

describe('defineLanguage utils', () => {
    it('Возвращает верные значения на краевых значениях', () => {
        expect(defineLanguage('')).toEqual('');
        expect(defineLanguage('Ru')).toEqual('ru');
        expect(defineLanguage()).toEqual('');
    });

    it('Верно мапит языки', () => {
        expect(defineLanguage('nn')).toEqual('no');
        expect(defineLanguage('Iw')).toEqual('he');
    });
});
