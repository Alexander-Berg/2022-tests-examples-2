package ru.yandex.metrika.locale;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.Arrays;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.util.locale.LocaleLangs;

import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertTrue;

/**
 * @author jkee
 */

public class LocaleGeobaseTest {
    LocaleGeobase geobase;
    @Before
    public void setUp() throws Exception {
        geobase = new LocaleGeobase();
        String geo =
                "Id\tParent\tType\tRuname\tTrname\tEnname\tUkname\tLat\tLon\tIso\n" +
                "10001\t10000\t1\tЕвразия\tAvrasya\tEurasia\tЄвразія\t56\t85\t\n" +
                "12345\t10000\t1\tЕвразия\tAvras22ya\tEurasia\tЄв22разія\t56\t85\t\n" +
                "166\t10001\t2\tСНГ\tBDT\tCIS\tСНД\t0\t0\t\n" +
                "112943\t207\t6\tКара-Балта\t\tKarabalta\t\t42.83\t73.859\t\n" ;
        InputStream stream = new ByteArrayInputStream(geo.getBytes());
        geobase.init(stream);

    }

    @Test
    public void testLocal() throws Exception {
        assertEquals("Евразия", geobase.idToLocal(LocaleLangs.RU, 10001));
        assertEquals("Avrasya", geobase.idToLocal(LocaleLangs.TR, 10001));
        assertEquals("Eurasia", geobase.idToLocal(LocaleLangs.EN, 10001));
        assertEquals("Евразия", geobase.idToLocal(LocaleLangs.UA, 10001));

        assertEquals("СНГ", geobase.idToLocal(LocaleLangs.RU, 166));
        assertEquals("BDT", geobase.idToLocal(LocaleLangs.TR, 166));
        assertEquals("CIS", geobase.idToLocal(LocaleLangs.EN, 166));
        assertEquals("СНГ", geobase.idToLocal(LocaleLangs.UA, 166));

        assertEquals("Кара-Балта", geobase.idToLocal(LocaleLangs.RU, 112943));
        assertEquals("Кара-Балта",  geobase.idToLocal(LocaleLangs.TR, 112943));
        assertEquals("Karabalta",  geobase.idToLocal(LocaleLangs.EN,  112943));
        assertEquals("Кара-Балта",  geobase.idToLocal(LocaleLangs.UA, 112943));

        assertTrue(Arrays.equals(new int[]{166}, geobase.localToId(LocaleLangs.RU, "СНГ")));
        assertTrue(Arrays.equals(new int[]{166}, geobase.localToId(LocaleLangs.TR, "BDT")));
        assertTrue(Arrays.equals(new int[]{166}, geobase.localToId(LocaleLangs.EN, "CIS")));
        assertTrue(Arrays.equals(new int[]{166}, geobase.localToId(LocaleLangs.UA, "СНГ")));

        assertTrue(Arrays.equals(new int[]{10001, 12345},   geobase.localToId(LocaleLangs.RU, "Евразия")));
        assertTrue(Arrays.equals(new int[]{10001, 12345},   geobase.localToId(LocaleLangs.EN, "Eurasia")));
        assertTrue(Arrays.equals(new int[]{10001, 12345},   geobase.localToId(LocaleLangs.UA, "Евразия")));

        assertTrue(Arrays.equals(new int[]{10001},          geobase.localToId(LocaleLangs.TR, "Avrasya")));

    }
}
