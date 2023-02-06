package ru.yandex.metrika.ui.maps.utils;

import junit.framework.Assert;
import org.junit.Test;

import ru.yandex.metrika.util.hash.ClickhouseHalfMD5;

/**
 * @author lemmsh
 * @since 4/15/14
 */
public class CHHashTest {

    @Test
    public void testHash() throws Exception {

        String url = "http://my.sendflowers.ru/user/customer/orders/";
        Assert.assertEquals("10882504796403317415", ClickhouseHalfMD5.decHalfMD5(url));
        Assert.assertEquals("97066C74501ABAA7", ClickhouseHalfMD5.hexHalfMD5(url).toUpperCase());

    }

    @Test
    public void testPrepareURL() throws Exception {
        Assert.assertEquals("http://www.asdf.com/asdf/asdf?from=12#part/", ClickhouseURLHash.prepareToHash("http://www.www.asdf.com/asdf/asdf?from=12&utm_source=1234&openstat_campaign=1234#part", true));
        Assert.assertEquals("http://www.asdf.com/asdf/asdf?from=12/", ClickhouseURLHash.prepareToHash("http://www.www.asdf.com/asdf/asdf?from=12&utm_source=1234&openstat_campaign=1234#part", false));
        Assert.assertEquals("http://www.asdf.com/asdf/asdf?from=12#part/", ClickhouseURLHash.prepareToHash("http://www.www.asdf.com/asdf/asdf?from=12&utm_source=1234#part", true));
        Assert.assertEquals("http://www.asdf.com/asdf/asdf?from=12/", ClickhouseURLHash.prepareToHash("http://www.www.asdf.com/asdf/asdf?from=12&utm_source=1234#part", false));
        Assert.assertEquals("http://asdf.com/asdf/asdf/", ClickhouseURLHash.prepareToHash("http://www.asdf.com/asdf/asdf?", false));
        Assert.assertEquals("http://asdf.com/asdf/asdf#part/", ClickhouseURLHash.prepareToHash("http://asdf.com/asdf/asdf?#part", true));
        Assert.assertEquals("http://eco-garden.info/index.php?route=product%2Fproduct&path=214&product_id=899/", ClickhouseURLHash.prepareToHash("http://eco-garden.info/index.php?route=product%2Fproduct&path=214&product_id=899", false));
        Assert.assertEquals("http://eco-garden.info/садовые-домики/", ClickhouseURLHash.prepareToHash("http://eco-garden.info/садовые-домики/", false));
        Assert.assertEquals("http://jetmoney.ru/request.html?amount=5 000&duration=10/", ClickhouseURLHash.prepareToHash("http://jetmoney.ru/request.html?amount=5 000&duration=10", false));
        Assert.assertEquals("http://graph.unick-soft.ru/?matrix=0, 1, 0\n1, 0, 0\n0, 1, 0/", ClickhouseURLHash.prepareToHash("http://graph.unick-soft.ru/?matrix=0, 1, 0\n1, 0, 0\n0, 1, 0", false));
        Assert.assertEquals("http://osmin.ru/Catalog/Products/варочные_поверхности/",ClickhouseURLHash.prepareToHash("http://osmin.ru/Catalog/Products/%D0%B2%D0%B0%D1%80%D0%BE%D1%87%D0%BD%D1%8B%D0%B5_%D0%BF%D0%BE%D0%B2%D0%B5%D1%80%D1%85%D0%BD%D0%BE%D1%81%D1%82%D0%B8/", false));
        Assert.assertEquals("http://communicat.tkat.ru/?mod=offers&category=communicat&product=ZTE BLADE GF3/",ClickhouseURLHash.prepareToHash("http://communicat.tkat.ru/?mod=offers&category=communicat&product=ZTE+BLADE+GF3", false));
        Assert.assertEquals("http://sendflowers.ru/rus/flowers-russia-moscow/special-special?%2Frus%2Fflowers-russia-moscow%2Fspecial-special=&price=0,3000/", ClickhouseURLHash.prepareToHash("http://sendflowers.ru/rus/flowers-russia-moscow/special-special?%2Frus%2Fflowers-russia-moscow%2Fspecial-special=&price=0,3000/", false));
        Assert.assertEquals("http://biohab.ru/index.php?/page/index.html/", ClickhouseURLHash.prepareToHash("http://biohab.ru/index.php?/page/index.html", false));
    }
}
