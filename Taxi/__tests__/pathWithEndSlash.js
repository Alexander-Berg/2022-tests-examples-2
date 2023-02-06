import pathWithEndSlash from '../pathWithEndSlash';

describe('server utils - pathWithEndSlash', () => {
    it('Для пустого значения должен вернуть /', () => {
        expect(pathWithEndSlash()).toEqual('/');
    });

    it('Для значения со слешов - возвращает его же', () => {
        expect(pathWithEndSlash('/')).toEqual('/');
    });

    it('Для значения без слеша - добавляет его', () => {
        expect(pathWithEndSlash('/page')).toEqual('/page/');
    });

    it('При наличии query - верно добавляет слеш', () => {
        expect(pathWithEndSlash('/page?id=1')).toEqual('/page/?id=1');
    });

    it('При наличии query и слеша - оставляет без изменений', () => {
        expect(pathWithEndSlash('/page/?id=1')).toEqual('/page/?id=1');
    });
});
