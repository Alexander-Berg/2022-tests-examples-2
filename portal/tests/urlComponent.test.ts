import { safeDecodeURIComponent, safeEncodeURIComponent } from '@lib/url/urlComponent';

describe('safeDecodeURIComponent', function() {
    test('декодит обычный url', function() {
        expect(safeDecodeURIComponent('')).toEqual('');
        expect(safeDecodeURIComponent('abcde')).toEqual('abcde');
        expect(safeDecodeURIComponent('%3Fa%3D1%26b%3D2')).toEqual('?a=1&b=2');
        expect(safeDecodeURIComponent('%D0%BC%D0%BE%D1%80%D0%B4%D0%B0%20%D1%80%D1%83%D0%BB%D0%B8%D1%82')).toEqual('морда рулит');
    });

    test('не падает с ошибкой', function() {
        expect(safeDecodeURIComponent('%E0%A4%A')).toBeNull();
    });
});

describe('safeEncodeURIComponent', function() {
    test('энкодит обычный url', function() {
        expect(safeEncodeURIComponent('')).toEqual('');
        expect(safeEncodeURIComponent('abcde')).toEqual('abcde');
        expect(safeEncodeURIComponent('?a=1&b=2')).toEqual('%3Fa%3D1%26b%3D2');
        expect(safeEncodeURIComponent('морда рулит')).toEqual('%D0%BC%D0%BE%D1%80%D0%B4%D0%B0%20%D1%80%D1%83%D0%BB%D0%B8%D1%82');
    });

    test('не падает с ошибкой', function() {
        expect(safeEncodeURIComponent('\uD800')).toBeNull();
    });
});
