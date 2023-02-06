import { labelFromHtml } from '../labelFromHtml';

describe('labelFromHtml', function() {
    test('Removing tag from html', function() {
        expect(labelFromHtml('Новогодние<br>чудеса с Алисой')).toEqual('Новогодние чудеса с Алисой');
        expect(labelFromHtml('<p>Новогодние</p><p>чудеса с Алисой</p>')).toEqual('Новогодние чудеса с Алисой');
        expect(labelFromHtml('<div>Новогодние</div><div>чудеса с Алисой</div>')).toEqual('Новогодние чудеса с Алисой');
        expect(labelFromHtml('<b>Новогодние</b> чудеса с Алисой')).toEqual('Новогодние чудеса с Алисой');
        expect(labelFromHtml('<span>Новогодние</span> чудеса с Алисой')).toEqual('Новогодние чудеса с Алисой');
    });
});
