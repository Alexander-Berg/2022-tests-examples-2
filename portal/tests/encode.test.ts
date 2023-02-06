import { htmlFilter, ltgtFilter } from '../encode';

describe('encode', () => {
    describe('htmlFilter', () => {
        test('не изменяет пустую строку', function() {
            expect(htmlFilter('')).toEqual('');
        });

        test('не изменяет текст', function() {
            expect(htmlFilter('text')).toEqual('text');
        });

        test('преобразует спецсимволы', function() {
            expect(htmlFilter('<div>')).toEqual('&lt;div&gt;');
            expect(htmlFilter('<div data-url="yandex/?text=123&abc">'))
                .toEqual('&lt;div data-url=&quot;yandex/?text=123&amp;abc&quot;&gt;');
        });
    });

    describe('ltgtFilter', function() {
        test('не изменяет пустую строку', function() {
            expect(ltgtFilter('')).toEqual('');
        });

        test('не изменяет текст', function() {
            expect(ltgtFilter('text')).toEqual('text');
        });

        test('преобразует спецсимволы', function() {
            expect(ltgtFilter('<div>')).toEqual('&lt;div&gt;');
            expect(ltgtFilter('<div data-url="yandex/?text=123&abc">'))
                .toEqual('&lt;div data-url="yandex/?text=123&abc"&gt;');
        });
    });
});
