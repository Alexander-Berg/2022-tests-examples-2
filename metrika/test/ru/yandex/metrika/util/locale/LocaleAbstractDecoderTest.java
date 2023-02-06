package ru.yandex.metrika.util.locale;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import com.google.common.collect.Lists;
import gnu.trove.map.TLongObjectMap;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

/**
 * @author jkee
 */

public class LocaleAbstractDecoderTest {
    LocaleAbstractDecoder decoder;
    Map<String, Map<String, long[]>> map;
    @Before
    public void setUp() throws Exception {
        map = new HashMap<>();
        for (String lang : LocaleLangs.getAvailableLangs()) {
            Map<String, long[]> localMap = new HashMap<>();
            map.put(lang, localMap);
        }
        decoder = new LocaleAbstractDecoder() {
            @Override
            protected Map<String, Map<String, long[]>> getMap(Object obj) {
                return map;
            }

            @Override
            protected Map<String, TLongObjectMap<String>> getEncodeMap(Object obj) {
                return null;
            }
        };
    }

    @Test
    public void testDecode() throws Exception {
        /*
        eq
        ne
        gt
        lt
        ge
        le
        sub
        nsub
        re
        nr
        * */
        map.get(LocaleLangs.EN).put("ololo",  new long[]{1, 2});
        map.get(LocaleLangs.EN).put("ololo2", new long[]{3});
        map.get(LocaleLangs.EN).put("3ololo", new long[]{4, 5, 6});
        Assert.assertArrayEquals(new long[]{1, 2}, decoder.eq(Collections.singletonList("ololo"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{3}, decoder.eq(Collections.singletonList("ololo2"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{1, 2, 4, 5, 6}, decoder.ne(Collections.singletonList("ololo2"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{1, 2, 3}, decoder.ge(Collections.singletonList("ololo"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{4, 5, 6}, decoder.le(Collections.singletonList("3ololo"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{3}, decoder.gt(Collections.singletonList("ololo"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{4, 5, 6}, decoder.lt(Collections.singletonList("ololo"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{1, 2, 3, 4, 5, 6}, decoder.sub(Collections.singletonList("ololo"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{1, 2, 3}, decoder.nsub(Collections.singletonList("3"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{1, 2, 3, 4, 5, 6}, decoder.re(Collections.singletonList(".*ololo.*"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{1, 2, 3}, decoder.nr(Collections.singletonList(".*3.*"), LocaleLangs.EN, null));

        Assert.assertArrayEquals(new long[]{1, 2}, decoder.in(Lists.newArrayList("ololo"), LocaleLangs.EN, null));
//        Assert.assertArrayEquals(new long[]{1, 2}, decoder.notIn(Lists.newArrayList("ololo"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{1, 2, 3}, decoder.in(Lists.newArrayList("ololo", "ololo2"), LocaleLangs.EN, null));
//        Assert.assertArrayEquals(new long[]{1, 2, 3}, decoder.notIn(Lists.newArrayList("ololo", "ololo2"), LocaleLangs.EN, null));
        Assert.assertArrayEquals(new long[]{1, 2, 3, 4, 5, 6}, decoder.in(Lists.newArrayList("ololo", "ololo2", "3ololo"), LocaleLangs.EN, null));
//        Assert.assertArrayEquals(new long[]{1, 2, 3, 4, 5, 6}, decoder.notIn(Lists.newArrayList("ololo", "ololo2", "3ololo"), LocaleLangs.EN, null));
    }

}
