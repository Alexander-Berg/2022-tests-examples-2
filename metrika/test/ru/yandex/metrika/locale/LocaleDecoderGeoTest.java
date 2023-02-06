package ru.yandex.metrika.locale;

import java.util.Arrays;
import java.util.Collections;

import com.google.common.collect.Lists;
import org.apache.commons.lang3.ArrayUtils;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.util.geobase.GeoBase;
import ru.yandex.metrika.util.geobase.RegionType;
import ru.yandex.metrika.util.locale.LocaleLangs;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

/**
 * @author jkee
 */
@Ignore("METRIQA-936")
public class LocaleDecoderGeoTest {
    LocaleDecoderGeo localeDecoderGeo;
    @Before
    public void setUp() throws Exception {
        localeDecoderGeo = new LocaleDecoderGeo();
        localeDecoderGeo.setGeoBase(new GeoBase());
        LocaleGeobase localeGeobase = new LocaleGeobase();
        localeGeobase.afterPropertiesSet();
        localeDecoderGeo.setLocaleGeobase(localeGeobase);
        localeDecoderGeo.setRegionType(RegionType.CITY);
        localeDecoderGeo.afterPropertiesSet();

    }

    @Test
    public void testName() throws Exception {
        System.out.println(Arrays.toString(localeDecoderGeo.eq(Collections.singletonList("Москва"), LocaleLangs.RU, null)));
        System.out.println(Arrays.toString(localeDecoderGeo.sub(Collections.singletonList("Астрахань"), LocaleLangs.RU, null)));
        assertTrue(ArrayUtils.contains(localeDecoderGeo.le(Collections.singletonList("Астрахань"),     LocaleLangs.RU, null), 37));
        assertFalse(ArrayUtils.contains(localeDecoderGeo.lt(Collections.singletonList("Астрахань"),    LocaleLangs.RU, null), 37));
        assertTrue(ArrayUtils.contains(localeDecoderGeo.sub(Collections.singletonList("Астрахань"),    LocaleLangs.RU, null), 37));
        assertFalse(ArrayUtils.contains(localeDecoderGeo.nsub(Collections.singletonList("Астрахань"),  LocaleLangs.RU, null), 37));
        assertTrue(ArrayUtils.contains(localeDecoderGeo.sub(Collections.singletonList("Astrahan"),     LocaleLangs.EN, null), 37));
        assertFalse(ArrayUtils.contains(localeDecoderGeo.nsub(Collections.singletonList("Astrahan"),   LocaleLangs.EN, null), 37));
        assertTrue(ArrayUtils.contains(localeDecoderGeo.sub(Collections.singletonList("Astrahan"),     LocaleLangs.EN, null), 37));
        assertFalse(ArrayUtils.contains(localeDecoderGeo.nsub(Collections.singletonList("Astrahan"),   LocaleLangs.EN, null), 37));

        assertArrayEquals(localeDecoderGeo.in(Lists.newArrayList("Астрахань", "Москва"), LocaleLangs.RU, null), new long[]{37, 213});
        assertArrayEquals(localeDecoderGeo.notIn(Lists.newArrayList("Астрахань", "Москва"), LocaleLangs.RU, null), new long[]{37, 213});
    }
}
