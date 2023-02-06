import { transliterate } from '../transliterate';

describe('transliterate', function() {
    it('should transliterate', function() {
        expect(transliterate('Человеко-месяц')).toEqual('CHeloveko-mesyac');
        expect(transliterate('Популярное')).toEqual('Populyarnoe');
        expect(transliterate('Для детей')).toEqual('Dlya detey');
        expect(transliterate('Найдётся всё')).toEqual('Naydetsya vse');
    });
});
