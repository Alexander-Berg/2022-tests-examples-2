import {MARKUP, LINK_PROTOCOLS, LINK_TARGET} from '../text-formatters';

const createTransformFirst = ({regExp, factory}) => text => factory(regExp.exec(text) || [], text => text);

describe('utils:text-formatters', () => {
    describe('MARKUP', () => {
        test('MARKUP.LINK target-_self', () => {
            const transformFirst = createTransformFirst(
                MARKUP.LINK({target: LINK_TARGET.SELF, allowedProtocols: [LINK_PROTOCOLS.HTTP]})
            );

            expect(transformFirst('((http://yandex.ru Вот ссылка на Яндекс))')).toBe(
                '<a target="_self" href="http://yandex.ru">Вот ссылка на Яндекс</a>'
            );
            expect(transformFirst('((http://yandex.ru))')).toBe(
                '<a target="_self" href="http://yandex.ru">http://yandex.ru</a>'
            );

            expect(transformFirst('((http://yandex.ru)) ((http://yandex.ru ссылка))')).toBe(
                '<a target="_self" href="http://yandex.ru">http://yandex.ru</a>'
            );
        });
        test('MARKUP.LINK target=_blank', () => {
            const transformFirst = createTransformFirst(
                MARKUP.LINK({target: LINK_TARGET.BLANK, allowedProtocols: [LINK_PROTOCOLS.HTTP]})
            );

            expect(transformFirst('((http://yandex.ru Вот ссылка на Яндекс))')).toBe(
                '<a target="_blank" href="http://yandex.ru">Вот ссылка на Яндекс</a>'
            );
            expect(transformFirst('((http://yandex.ru))')).toBe(
                '<a target="_blank" href="http://yandex.ru">http://yandex.ru</a>'
            );

            expect(transformFirst('((http://yandex.ru)) ((http://yandex.ru ссылка))')).toBe(
                '<a target="_blank" href="http://yandex.ru">http://yandex.ru</a>'
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
                '<a target="_self" href="http://www.yandex.ru">яндекс</a>'
            );
        });
    });
});
