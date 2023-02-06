package ru.yandex.metrika.util.url;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Arrays;

import org.junit.Test;

import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

/**
 * Created by IntelliJ IDEA.
 * User: igorbachev
 * Date: 2/7/12
 * Time: 1:00 PM
 * To change this template use File | Settings | File Templates.
 */
public class NormalizedURITest {

    @Test
    public void test111() throws URISyntaxException {
        System.out.println(NormalizedURI.translateToInternalFormat(("http://yasli-shop.ru/detskaja-krovatka-chu-cha-majatnik-poperechnyj-cvet-vishnja.html?utm_source=yandex&utm_medium=market&utm_campaign=%D0%B4%D0%B5%D1%82%D1%81%D0%BA%D0%B0%D1%8F+%D0%BA%D1%80%D0%BE%D0%B2%D0%B0%D1%82%D0%BA%D0%B0+%D0%93%D0%B0%D0%BD%D0%B4%D1%8B%D0%B&_openstat=bWFya2V0LnlhbmRleC5ydTvQtNC10YLRgdC60LDRjyDQutGA0L7QstCw0YLQutCwINCT0LDQvdC00YvQu9GP0L0g0KfRgy3Rhzs4OTU3OTY2MTk7"
        )));

        System.out.println(NormalizedURI.translateToInternalFormat(("http://yasli-shop.ru/ololo,ololo%2Cololo"
        )));

    }

    @Test
    public void testMETRIKASUPP5152() throws URISyntaxException {
        System.out.println(NormalizedURI.translateToInternalFormat(("http://reborsa.ru/leo-ventoni?yclid=5865920388254086384#instock=on&manufacturer_id=35&page=1&limit=24&route=product%2Fmanufacturer%2Finfo&categories[]=125"
        )));

    }

    @Test
    public void test111111() throws Exception {
        Log4jSetup.basicSetup();
        String url = "http://www.uzbnews.ru/news/quot_qalb_ko_39_zi_quot_yangi_o_39_zbek_kino_2012_yuklash_kalb_kuzi_jangi_uzbek_kino_skachat/2012-02-16-1272#iit=1337598466203&tmr=load%3D1337598463906%26core%3D1337598466156%26main%3D1337598466171%26ifr%3D1337598466203&cb=0&cdn=0&chr=utf-8&kw=Uzbek%20kino%202011-2012%2CHind%20kinolari%20uzbek%20tilida%2C%D0%A3%D0%B7%D0%B1%D0%B5%D0%BA%20%D0%BA%D0%B8%D0%BD%D0%BE%202011-2012%2C%D0%A5%D0%B8%D0%BD%D0%B4%20%D0%BA%D0%B8%D0%BD%D0%BE%D0%BB%D0%B0%D1%80%D0%B8%20%D1%83%D0%B7%D0%B1%D0%B5%D0%B";
        NormalizedURI normalizedURI = new NormalizedURI(url);
        System.out.println(normalizedURI);
        System.out.println(NormalizedURI.translateToInternalFormat(url));
        System.out.println(NormalizedURI.translateToExternalFormat(url));
        System.out.println(normalizedURI.toASCIIString());
        System.out.println(normalizedURI.toUnicodeString());
        System.out.println(normalizedURI.toUnicodeString());
    }

    @Test
    public void test1111() throws URISyntaxException {
        String url = "http://www.google.com.ua/url?sa=t&rct=j&q=%D0%B0%D0%BC%D1%84+%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7+%D1%86%D0%B2%D0%B5%D1%82%D0%BE%D0%B2&source=web&cd=1&ved=0CIsBEBYwAA&url=http://www.sendflowers.ru/&ei=SZmzT-P4Ncvs-gaxp6TpCA&usg=AFQjCNGe12ERTuTvRREcQzWeh_1lpV9Nag&cad=rjt";
        String url2 = "http://www.google.com.ua/url?q=%D0%B0%D0%BC%D1%84+%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7+%D1%86%D0%B2%D0%B5%D1%82%D0%BE%D0%B2&source=web&cd=1&ved=0CIsBEBYwAA&url=http://www.sendflowers.ru/&ei=SZmzT-P4Ncvs-gaxp6TpCA&usg=AFQjCNGe12ERTuTvRREcQzWeh_1lpV9Nag&cad=rjt";
        String url3 = "http://www.google.com.ua/url?sa=t&rct=j&q=%D0%B0%D0%BC%D1%84+%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7+%D1%86%D0%B2%D0%B5%D1%82%D0%BE%D0%B2";
        NormalizedURI normalizedURI1 = new NormalizedURI(url);
        NormalizedURI normalizedURI2 = new NormalizedURI(url2);
        NormalizedURI normalizedURI3 = new NormalizedURI(url3);
        assertEquals("%D0%B0%D0%BC%D1%84+%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7+%D1%86%D0%B2%D0%B5%D1%82%D0%BE%D0%B2", normalizedURI1.getParameterValue("q"));
        assertEquals("%D0%B0%D0%BC%D1%84+%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7+%D1%86%D0%B2%D0%B5%D1%82%D0%BE%D0%B2", normalizedURI2.getParameterValue("q"));
        assertEquals("%D0%B0%D0%BC%D1%84+%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7+%D1%86%D0%B2%D0%B5%D1%82%D0%BE%D0%B2", normalizedURI3.getParameterValue("q"));


    }

    @Test
    public void testRemoveParameter() throws URISyntaxException {
        String url = "http://google.com.ua/url?sa=t&rct=j&q=zzzzz&source=web&cd=1&ved=0CIsBEBYwAA&url=http://www.sendflowers.ru/&ei=SZmzT-P4Ncvs-gaxp6TpCA&usg=AFQjCNGe12ERTuTvRREcQzWeh_1lpV9Nag&cad=rjt";
        NormalizedURI normalizedURI1 = new NormalizedURI(url);
        normalizedURI1.removeParameter("ved");
        assertEquals("http://google.com.ua/url?sa=t&rct=j&q=zzzzz&source=web&cd=1&url=http://www.sendflowers.ru/&ei=SZmzT-P4Ncvs-gaxp6TpCA&usg=AFQjCNGe12ERTuTvRREcQzWeh_1lpV9Nag&cad=rjt", normalizedURI1.toASCIIString());
        normalizedURI1.removeParameter("sa");
        assertEquals("http://google.com.ua/url?rct=j&q=zzzzz&source=web&cd=1&url=http://www.sendflowers.ru/&ei=SZmzT-P4Ncvs-gaxp6TpCA&usg=AFQjCNGe12ERTuTvRREcQzWeh_1lpV9Nag&cad=rjt", normalizedURI1.toASCIIString());
        String url2 = "http://google.com.ua/";
        NormalizedURI normalizedURI2 = new NormalizedURI(url2);
        normalizedURI2.removeParameter("sa");
        assertEquals("http://google.com.ua/", normalizedURI2.toASCIIString());

    }

    private static String trimUtf(String s, int len) {
        if (s.length() > len) {
            s = s.substring(0, len);
            if (s.charAt(s.length() - 1) == '%') {
                s = s.substring(0, s.length() - 1);
            } else if (s.charAt(s.length() - 2) == '%') {
                s = s.substring(0, s.length() - 2);
            }
            if (s.endsWith("%D0") || s.endsWith("%D1")) {  // первый байт utf-8 символа тоже дропаем, поскольку от него толку нет.
                s = s.substring(0, s.length() - 3);
            }
        }
        return s;
    }

    @Test
    public void testTL() throws URISyntaxException {
        final String url = "http://en.wikipedia.org:123123/wiki/Internationalized_domain_name?12312ad asdf & ajl ";
        final int ITERATIONS = (int) 1e+6;
        for (int i = 0; i < ITERATIONS; ++i) {
            NormalizedURI nURI = new NormalizedURI(url);
        }
    }

    @Test
    public void test() throws URISyntaxException {
        String url = "http://account.forex4you.org/ru/stat/?affid=9b43570&page_title=http://www.forex4you.com/&gclid=CJHc59P3vqgCFYIc6wodxTYKqA&gclid=CJHc59P3vqgCFYIc6wodxTYKqA&referer=http://www.forex4you.com/&Faffid=D9b43570#sdfasdf";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("http", uri.getScheme());
        assertEquals("sdfasdf", uri.getFragment());
        assertNull(uri.getFrom());
        assertEquals("account.forex4you.org", uri.getHost());
        assertEquals("/ru/stat/", uri.getPath());
        assertEquals(-1, uri.getPort());
        assertEquals("affid=9b43570&page_title=http://www.forex4you.com/&referer=http://www.forex4you.com/&Faffid=D9b43570", uri.getQuery());
        assertNull(uri.getOpenStat());
        System.out.println(Arrays.toString(uri.getUtm()));
    }

    @Test
    public void testRussianFrom() throws URISyntaxException {
        String url = "http://account.forex4you.org/ru/stat/?affid=9b43570&page_title=http://www.forex4you.com/&gclid=CJHc59P3vqgCFYIc6wodxTYKqA&gclid=CJHc59P3vqgCFYIc6wodxTYKqA&referer=http://www.forex4you.com/&Faffid=D9b43570&from=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0#sdfasdf";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("http", uri.getScheme());
        assertEquals("sdfasdf", uri.getFragment());
        assertEquals("Москва", uri.getFrom());
        assertEquals("account.forex4you.org", uri.getHost());
        assertEquals("/ru/stat/", uri.getPath());
        assertEquals(-1, uri.getPort());
        assertEquals("affid=9b43570&page_title=http://www.forex4you.com/&referer=http://www.forex4you.com/&Faffid=D9b43570", uri.getQuery());
        assertNull(uri.getOpenStat());
        System.out.println(Arrays.toString(uri.getUtm()));
    }

    @Test
    public void testWhite() throws Exception {
        NormalizedURI nu = new NormalizedURI("http://bash.im/white scape", NORMALIZATION_PARAMS);
        assertEquals("http://bash.im/white+scape", nu.toASCIIString());
        URI proxyUri = new URI(nu.toASCIIString());
        assertEquals("http://bash.im/white+scape", proxyUri.toASCIIString());
        URI proxyUri2 = new URI(new NormalizedURI("http://bash.im/white scape", NORMALIZATION_PARAMS).toASCIIString());
        assertEquals("http://bash.im/white+scape", proxyUri2.toASCIIString());
    }

    private static final UriNormalizationParams NORMALIZATION_PARAMS = new UriNormalizationParams() {
        @Override
        public boolean isModificationProhibited() {
            return true;
        }

        @Override
        public boolean isTrimWww() {
            return false;
        }

    };

    @Test
    public void test1() throws URISyntaxException {
        String url = "http://www.this-site.ru/asdf?a=b&c=d";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("a=b&c=d", uri.getQuery());
    }

    @Test(expected = URISyntaxException.class)
    public void test2() throws URISyntaxException {
        NormalizedURI uri = new NormalizedURI("scheme://username:password@domain:123/path?query_string#fragment_id");
    }

    @Test
    public void testURIWithSchemeHost() throws URISyntaxException {
        String url = "http://yandex.ru";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("http", uri.getScheme());
        assertEquals("yandex.ru", uri.getHost());
    }

    @Test
    public void testURIWithSchemeHostPort() throws URISyntaxException {
        String url = "http://yandex.ru:8080";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("http", uri.getScheme());
        assertEquals("yandex.ru", uri.getHost());
        assertEquals(8080, uri.getPort());
    }

    @Test
    public void testURIWithSchemeHostPortPath() throws URISyntaxException {
        String url = "http://yandex.ru:8080/some/path/with/data.html";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("http", uri.getScheme());
        assertEquals("yandex.ru", uri.getHost());
        assertEquals(8080, uri.getPort());
        assertEquals("/some/path/with/data.html", uri.getPath());
    }

    @Test
    public void testEmptyPath() throws URISyntaxException {
        String url = "http://yandex.ru";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("/", uri.getPath());
    }

    @Test
    public void testURIWithSchemeHostPortPathQuery() throws URISyntaxException {
        String url = "http://yandex.ru:8080/some/path/with/data.html?param1=1&param2=2&param3=ads";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("http", uri.getScheme());
        assertEquals("yandex.ru", uri.getHost());
        assertEquals(8080, uri.getPort());
        assertEquals("/some/path/with/data.html", uri.getPath());
        assertEquals("param1=1&param2=2&param3=ads", uri.getQuery());
    }

    @Test
    public void testURIWithSchemeHostPortPathQueryFragment() throws URISyntaxException {
        String url = "http://yandex.ru:8080/some/path/with/data.html?param1=1&param2=2&param3=ads#some_point";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("http", uri.getScheme());
        assertEquals("yandex.ru", uri.getHost());
        assertEquals(8080, uri.getPort());
        assertEquals("/some/path/with/data.html", uri.getPath());
        assertEquals("param1=1&param2=2&param3=ads", uri.getQuery());
        assertEquals("some_point", uri.getFragment());
    }

    @Test
    public void testURL1() throws URISyntaxException {
        String url = "http://allegro.kz/nokia-n9-kct-u-nas-cena-sensaciya-i2085355184.html?&utm_medium=start_date30.01.12&utm_campaign=goods_link";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("", uri.getQuery());
    }

    @Test
    public void testURL2() throws URISyntaxException {
        String url = "consultantplus://offline/main?base=LAW;n=112189;fld=134;dst=100076";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("base=LAW;n=112189;fld=134;dst=100076", uri.getQuery());
    }

    @Test
    public void testNoPortNoPathHasParams() throws URISyntaxException {
        String url = "https://yandex.ru?param=1&p=w";
        NormalizedURI uri = new NormalizedURI(url);
        assertEquals("param=1&p=w", uri.getQuery());
    }

    @Test(expected = URISyntaxException.class)
    public void testAboutBlankUrl() throws URISyntaxException {
        String url = "about:blank";
        NormalizedURI uri = new NormalizedURI(url);
    }

    @Test(expected = URISyntaxException.class)
    public void testEmpryHost() throws URISyntaxException {
        String url = "http://";
        NormalizedURI uri = new NormalizedURI(url);
    }

    @Test
    public void testTranslateToInternalFormatWithEscapedSymbols() {
        String url1 = "http://androidtalk.ru/phones/?os[]=609";
        String url2 = "http://androidtalk.ru/phones/?os%5B%5D=609";

        String ret1 = NormalizedURI.translateToInternalFormat(url1);
        String ret2 = NormalizedURI.translateToInternalFormat(url2);

        assertEquals(ret1, ret2);
    }

    @Test
    public void testTranslateToInternalFormatWithEscapedSymbolsAndLatinLetter() {
        String url1 = "http://androidtalk.ru/phones/?os[]=609";
        String url2 = "http://androidtalk.ru/phones/?%6F%73%5B%5D=609";

        String ret1 = NormalizedURI.translateToInternalFormat(url1);
        String ret2 = NormalizedURI.translateToInternalFormat(url2);

        assertEquals(ret1, ret2);
    }

    @Test
    public void testLowerCaseEscapedConversion() throws Exception {
        UriNormalizationParams params = new UriNormalizationParams() {

            @Override
            public boolean isTrimWww() {
                return false;
            }

            @Override
            public boolean encodeSpaceAsPlus() {
                return false;
            }
        };
        String url1 = "http://apteka.vl.ru/search/%d0%be%d1%82%20%d0%ba%d0%be%d0%bc%d0%b0%d1%80%d0%be%d0%b2/title/";
        String url2 = "http://apteka.vl.ru/search/%D0%BE%D1%82%20%D0%BA%D0%BE%D0%BC%D0%B0%D1%80%D0%BE%D0%B2/title/";

        String url3 = "http://yasli-shop.ru/ololo,ololo%2Cololo%2C";
        String url4 = "http://yasli-shop.ru/ololo,ololo%2Cololo%2";

        String ret1 = url2;
        String ret2 = new NormalizedURI(url1,params).toASCIIString();
        assertEquals(ret1,ret2);

        assertEquals(url3, new NormalizedURI(url3,params).toASCIIString());
        assertEquals(url4, new NormalizedURI(url4,params).toASCIIString());
    }

    //
    @Test
    public void testCounter25351574() throws Exception {
        {
            String url = "http://клининговая-компания-в-спб.рф/?from=y&stc=spb&stt=клининговая%компания";
            NormalizedURI n = new NormalizedURI(url);
            System.out.println("n = " + n.toASCIIString());
        }

    }

    @Test
    public void testURLEncodedDomain() throws Exception {
                UriNormalizationParams params = new UriNormalizationParams() {

                    @Override
            public boolean isTrimWww() {
                return false;
            }


                    @Override
            public boolean encodeSpaceAsPlus() {
                return false;
            }
        };
        String url1 = "http://моймалыш.su/";
        String url2 = "http://xn--80arhbbk8exa.su/";
        String ret2 = new NormalizedURI(url1,params).toASCIIString();
        String ret1 = new NormalizedURI(ret2,params).toUnicodeString();

        assertEquals(url2,ret2);
        assertEquals(url1,ret1);

    }

    @Test
    //METRIKASUPP-5268
    public void testPipe() throws Exception{
        NormalizedURI normalizedURI = new NormalizedURI("http://hello.org/yo/?abc=h|123|", NORMALIZATION_PARAMS);
        assertEquals("http://hello.org/yo/?abc=h%7C123%7C",normalizedURI.toASCIIString());
    }
}
