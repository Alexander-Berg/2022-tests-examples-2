import {MARKUP, LINK_PROTOCOLS, LINK_TARGET} from '../text-formatters';

const createTransformFirst = ({regExp, factory}) => text => factory(regExp.exec(text) || [], text => text);

describe('utils:text-formatters', () => {
    describe('MARKUP', () => {
        test('MARKUP.LINK target-_self', () => {
            const transformFirst = createTransformFirst(
                MARKUP.LINK({target: LINK_TARGET.SELF, allowedProtocols: [LINK_PROTOCOLS.HTTP]})
            );

            expect(transformFirst('((http://yandex.ru Вот ссылка на Яндекс))')).toBe(
                '<a rel="noopener" target="_self" href="http://yandex.ru">Вот ссылка на Яндекс</a>'
            );
            expect(transformFirst('((http://yandex.ru))')).toBe(
                '<a rel="noopener" target="_self" href="http://yandex.ru">http://yandex.ru</a>'
            );

            expect(transformFirst('((http://yandex.ru)) ((http://yandex.ru ссылка))')).toBe(
                '<a rel="noopener" target="_self" href="http://yandex.ru">http://yandex.ru</a>'
            );
        });
        test('MARKUP.LINK target=_blank', () => {
            const transformFirst = createTransformFirst(
                MARKUP.LINK({target: LINK_TARGET.BLANK, allowedProtocols: [LINK_PROTOCOLS.HTTP]})
            );

            expect(transformFirst('((http://yandex.ru Вот ссылка на Яндекс))')).toBe(
                '<a rel="noopener" target="_blank" href="http://yandex.ru">Вот ссылка на Яндекс</a>'
            );
            expect(transformFirst('((http://yandex.ru))')).toBe(
                '<a rel="noopener" target="_blank" href="http://yandex.ru">http://yandex.ru</a>'
            );

            expect(transformFirst('((http://yandex.ru)) ((http://yandex.ru ссылка))')).toBe(
                '<a rel="noopener" target="_blank" href="http://yandex.ru">http://yandex.ru</a>'
            );
        });
        test('MARKUP.LINK empty target', () => {
            const transformFirst = createTransformFirst(
                MARKUP.LINK({allowedProtocols: [LINK_PROTOCOLS.HTTP, 'yandextaxi:', 'tel:']})
            );

            expect(transformFirst('((http://yandex.ru Вот ссылка на Яндекс))')).toBe(
                '<a rel="noopener" target="" href="http://yandex.ru">Вот ссылка на Яндекс</a>'
            );
            expect(transformFirst('((http://yandex.ru))')).toBe(
                '<a rel="noopener" target="" href="http://yandex.ru">http://yandex.ru</a>'
            );

            expect(transformFirst('((http://yandex.ru)) ((http://yandex.ru ссылка))')).toBe(
                '<a rel="noopener" target="" href="http://yandex.ru">http://yandex.ru</a>'
            );

            expect(transformFirst('((yandextaxi://addpromo?id=124 ваш промик))')).toBe(
                '<a rel="noopener" target="" href="yandextaxi://addpromo?id=124">ваш промик</a>'
            );

            expect(transformFirst('((tel:+79771430000 звони))')).toBe(
                '<a rel="noopener" target="" href="tel:+79771430000">звони</a>'
            );
        });
        test('MARKUP.LINK target as object', () => {
            const transformFirst = createTransformFirst(
                MARKUP.LINK({
                    allowedProtocols: [LINK_PROTOCOLS.HTTP],
                    target: {
                        'forms.yandex.ru': LINK_TARGET.SELF,
                        default: LINK_TARGET.BLANK
                    }
                })
            );

            expect(transformFirst('((http://yandex.ru Вот ссылка на Яндекс))')).toBe(
                '<a rel="noopener" target="_blank" href="http://yandex.ru">Вот ссылка на Яндекс</a>'
            );
            expect(transformFirst('((http://forms.yandex.ru/124))')).toBe(
                '<a rel="noopener" target="_self" href="http://forms.yandex.ru/124">http://forms.yandex.ru/124</a>'
            );

            expect(transformFirst('((http://forms.yandex.ru?id=124))')).toBe(
                '<a rel="noopener" target="_self" href="http://forms.yandex.ru?id=124">http://forms.yandex.ru?id=124</a>'
            );
        });
        test('MARKUP.BOLD', () => {
            const transformFirst = createTransformFirst(MARKUP.BOLD());

            expect(transformFirst('**Вот это жирненько**')).toBe('<b>Вот это жирненько</b>');
        });
        test('TXI-6966', () => {
            const transformFirst = createTransformFirst(
                MARKUP.LINK({target: LINK_TARGET.SELF, allowedProtocols: [LINK_PROTOCOLS.HTTP]})
            );

            const XSSScript = '((<script>alert``</script> плохаяссылка))';
            const XSSJavascript1 = '((javascript:alert`` плохаяссылка))';
            const XSSJavascript2 = '((jAvAscript:alert`` плохаяссылка))';
            const XSSJavascript3 = '((j&NewLine;avascript:alert() плохаяссылка))';
            const unallowedProtocolFTP = '((ftp://ftp.yandex.ru плохаяссылка))';
            const allowedProtocolHTTP = '((http://www.yandex.ru яндекс))';

            expect(transformFirst(XSSScript)).toBe('');

            expect(transformFirst(XSSJavascript1)).toBe('');

            expect(transformFirst(XSSJavascript2)).toBe('');

            expect(transformFirst(XSSJavascript3)).toBe('');

            expect(transformFirst(unallowedProtocolFTP)).toBe('');

            expect(transformFirst(allowedProtocolHTTP)).toBe(
                '<a rel="noopener" target="_self" href="http://www.yandex.ru">яндекс</a>'
            );
        });
    });
});
