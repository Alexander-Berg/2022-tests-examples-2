import parseClasses from '../parseClasses';

describe('parseClasses utils', () => {
    it('Возвращает undefined если агнумент не строка', () => {
        expect(parseClasses()).toEqual(undefined);
        expect(parseClasses(1)).toEqual(undefined);
        expect(parseClasses('')).toEqual(undefined);
    });

    it('Возвращает список тарифов из строки', () => {
        const expectResult = ['a', 'b', 'c'];
        expect(parseClasses('a,b,c')).toEqual(expectResult);
        expect(parseClasses('a;b;c')).toEqual(expectResult);
        expect(parseClasses('a ;b ;c ')).toEqual(expectResult);
        expect(parseClasses('a ,b ,c ')).toEqual(expectResult);
    });
});
