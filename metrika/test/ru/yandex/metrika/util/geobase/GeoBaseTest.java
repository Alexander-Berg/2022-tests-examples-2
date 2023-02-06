package ru.yandex.metrika.util.geobase;

import java.util.Optional;

import org.junit.Test;

import static junit.framework.Assert.assertFalse;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * @author jkee
 */
public class GeoBaseTest {

    @Test
    public void testName() throws Exception {
        GeoBase geoBase = new GeoBase();
        assertEquals(225, geoBase.getParentForType(1, RegionType.COUNTRY).get().getId());
        assertEquals(225, geoBase.getParentForType(225, RegionType.COUNTRY).get().getId());
        assertEquals(Optional.<Region>empty(), geoBase.getParentForType(10001, RegionType.COUNTRY));

    }

    @Test
    public void testLayers() throws Exception {
        GeoBase geoBase = new GeoBase();
        assertTrue(geoBase.getByRegionType().get(RegionType.COUNTRY).containsKey(225));
        assertFalse(geoBase.getByRegionType().get(RegionType.CITY).containsKey(225));
    }

    @Test
    public void testRoot() throws Exception {
        GeoBase geoBase = new GeoBase();
        for(int i = 0; i < 200000; i++) {
            assertEquals("for region "+i, geoBase.getRootOld(i), geoBase.getRoot(i));
        }
    }

}
