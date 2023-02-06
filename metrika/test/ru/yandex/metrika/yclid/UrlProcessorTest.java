package ru.yandex.metrika.yclid;

import java.util.Date;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

@Ignore
public class UrlProcessorTest {

    private UrlProcessor processor;

    @Before
    public void setUp() throws Exception {
        processor = new UrlProcessor();
    }

    @Test
    public void testSubmitCheck() throws Exception {
//        String encoded = URLEncoder.encode("http://townmoney.ru/about-us/contacts?utm_campaign=Yandex_Business_Moscow_CN&utm_medium=YandexDirect_CPC&utm_source=YandexDirect_search_CPC&utm_content=360595952&utm_term={PHRASE}", "UTF-8");
//        URI uri = new URI(encoded);
//
//        URL url = new URL("http://townmoney.ru/about-us/contacts?utm_campaign=Yandex_Business_Moscow_CN&utm_medium=YandexDirect_CPC&utm_source=YandexDirect_search_CPC&utm_content=360595952&utm_term={PHRASE}");
//
//        String badUri = "http://calc.rockwool.ru/?utm_source=ya_direct&utm_medium=cpc&utm_campaign=competitors_isospan_dop4&utm_content=#(not+set)#&x={ASDF}";
//        String badUri2 = "http://nebo.ru/catalog/earrings/izumrud/sale?utm_medium=cpc&utm_source=yandex.direct&utm_campaign=Moskva%2BStone%2BIzumrud|7688225&utm_content=kw|%7BPHRASE%7D|pos|%7BPTYPE%7D%7BPOS%7D|src_type|%7BSTYPE%7D|src|%7BSRC%7D|ql|Vesennie_skidki|&advert_id=camp_id|7688225|ad_id|2448";
//        System.out.println((new NormalizedURI(badUri)).toASCIIString());
//        //System.out.println((new URI(badUri)).toASCIIString());
//
//        UriProvider yclidProvider1 = new UriProvider();
//
//        System.out.println(badUri2);
//        System.out.println(yclidProvider1.withYclid(yclidProvider1.parseUri(badUri2)));
//        System.out.println(yclidProvider1.withoutYclid(yclidProvider1.parseUri(badUri2)));
//
//        System.out.println(badUri);
//        System.out.println(yclidProvider1.withYclid(yclidProvider1.parseUri(badUri)));
//        System.out.println(yclidProvider1.withoutYclid(yclidProvider1.parseUri(badUri)));
//
//        System.out.println(yclidProvider1.withYclid(yclidProvider1.parseUri("http://dostavka-krd.ru/menu.php?p=5#0Американская пицца")));
//
//        System.out.println(tryExtractDomain("Malformed escape pair at index 254: http://xn----7sbba7adelfcpyg8b.xn--p1ai?utm_source=yandex&utm_medium=cpc&utm_campaign=mozaika&utm_content=%d0%9f%d0%bb%d0%b8%d1%82%d0%ba%d0%b0_%d0%bc%d0%be%d0%b7%d0%b0%d0%b8%d0%ba%d0%b0_%d0%b4%d0%bb%d1%8f_%d0%b2%d0%b0%d0%bd%d0%bd%d0%be%d0%b9_%d0%ba%d0%be%/"));

            final Optional<CompletableFuture<ResultRow>> result =
                    processor.submitCheck(
                            new DataRow(
                                    1,
                                    1,
                                    new Date(),
                                    "http://www.itmgroup.ru/prices.htm?country=Thailand&dep=1"
                            )
                    );
            final ResultRow row = result.get().get();
            System.out.println(row);

    }
}
