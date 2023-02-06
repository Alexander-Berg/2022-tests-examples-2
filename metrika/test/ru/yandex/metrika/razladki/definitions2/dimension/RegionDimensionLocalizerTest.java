package ru.yandex.metrika.razladki.definitions2.dimension;

import java.util.List;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.management.radar.RegionDimensionLocalizer;
import ru.yandex.metrika.locale.LocaleGeobase;
import ru.yandex.metrika.radar.address.Address;
import ru.yandex.metrika.radar.segments.SegmentableVisit;
import ru.yandex.metrika.util.geobase.GeoBase;

import static junit.framework.Assert.assertEquals;

/**
 * @author jkee
 */
public class RegionDimensionLocalizerTest {

    private RegionDimensionLocalizer regionDimension;

    @Before
    public void setUp() throws Exception {
        regionDimension = new RegionDimensionLocalizer();
        regionDimension.setGeoBase(new GeoBase());
        LocaleGeobase localeGeobase = new LocaleGeobase();
        localeGeobase.afterPropertiesSet();
        regionDimension.setLocaleGeobase(localeGeobase);
        regionDimension.afterPropertiesSet();


    }

    @Test
    public void testExternal() throws Exception {

        /*<region id="187" name="Украина" type="3" parent="166">
          <region id="20528" name="Север" type="2" parent="187"> WTF WTF WTF
            <region id="20551" name="Черниговская область" type="5" parent="20528">
              <region id="24851" name="Щорский район" type="10" parent="20551">
                <region id="28577" name="Хотуничи" type="6" parent="24851"/>*/

        Address address = regionDimension.getPath(new SegmentableVisit() {
            @Override
            public int getRegionId() {
                return 28577;
            }

            @Override
            public int getTrafficSourceId() {
                return 2;
            }

            @Override
            public int getSearchEngineId() {
                return 12;
            }

            @Override
            public int getAdvEngineId() {
                return 0;
            }

            @Override
            public boolean isNewVisit() {
                return false;
            }

            @Override
            public String getStartPage() {
                return "http://ololo.ru";
            }
        });

        List<String> string = regionDimension.toExternalStringArray(address, "ru");
        assertEquals(3, string.size());
        assertEquals("Украина", string.get(0));
        assertEquals("Черниговская область", string.get(1));
        assertEquals("Хотуничи", string.get(2));

        System.out.println(string);

        Address backAddress = regionDimension.fromExternalStringArray(string, "ru");

        assertEquals(address, backAddress);




    }
}
