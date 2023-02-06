package ru.yandex.autotests.morda.exports.tests.utils;

import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;
import ru.yandex.autotests.morda.exports.tests.ExportsTestsProperties;
import ru.yandex.qatools.geobase.Geobase;
import ru.yandex.qatools.geobase.beans.GeobaseRegionData;

import java.io.IOException;
import java.util.regex.Pattern;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 04.03.14
 */
public class MapsUtils {

    private static final ExportsTestsProperties CONFIG = new ExportsTestsProperties();

    private static final String MAPS_WITH_SPN_PATTERN = ".*ll=([^&]*).*spn=([^&]*).*";
    private static final String MAPS_WITH_ZOOM_PATTERN = ".*ll=([^&]*).*z=([^&\"]*).*";
    private static final String MAPS_SHORT_PATTERN = ".*//maps\\.yandex\\..*/\\-/.*";

    public static MapsArea getMapsArea(String url) {
        if (url.matches(MAPS_WITH_SPN_PATTERN)) {
            return getMapsWithSpn(url);
        } else if (url.matches(MAPS_WITH_ZOOM_PATTERN)) {
            return getMapsWithZoom(url);
        } else if (url.matches(MAPS_SHORT_PATTERN)) {
            return getMapsShort(url);
        } else {
            throw new RuntimeException("Failed to get MapsArea from " + url);
        }
    }

    private static MapsArea getMapsWithSpn(String url) {
        Pattern pattern = Pattern.compile(MAPS_WITH_SPN_PATTERN);
        java.util.regex.Matcher m = pattern.matcher(url);
        if (m.matches()) {
            String[] ll = m.group(1).split("%2C");
            String[] spn = m.group(2).split("%2C");
            return MapsArea.createMapsArea(ll[0], ll[1], spn[0], spn[1]);
        }
        throw new RuntimeException("Failed to get MapsArea from " + url);
    }

    private static MapsArea getMapsWithZoom(String url) {
        Pattern pattern = Pattern.compile(MAPS_WITH_ZOOM_PATTERN);
        java.util.regex.Matcher m = pattern.matcher(url);
        if (m.matches()) {
            String[] ll = m.group(1).split("%2C");
            Double[] spn = zToSpn(Integer.parseInt(m.group(2)));
            return MapsArea.createMapsArea(ll[0], ll[1], spn[0], spn[1]);
        }
        throw new RuntimeException("Failed to get MapsArea from " + url);
    }

    private static MapsArea getMapsShort(String url) {
        String newUrl = url.replaceAll("\\.ua|\\.by|\\.kz", ".ru");
        HttpClient client = new DefaultHttpClient();
        HttpGet get = new HttpGet(url);
        String response = null;
        try {
            response = EntityUtils.toString(client.execute(get).getEntity())
                    .replaceAll("\n", "");
            System.out.println(response);
            if (response.matches(MAPS_WITH_SPN_PATTERN)) {
                return getMapsWithSpn(response);
            } else if (response.matches(MAPS_WITH_ZOOM_PATTERN)) {
                return getMapsWithZoom(response);
            }
        } catch (IOException ignore) {
        }
        throw new RuntimeException("Failed to get MapsArea from " + url);
    }

    private static Double[] zToSpn(int z) {
        Double[] res = new Double[]{360.0, 110.0};
        while (z - 2 > 0) {
            res[0] /= 2;
            res[1] /= 2;
            z--;
        }
        return res;
    }

    public static MapsArea getLocation(int gid) {
        GeobaseRegionData region = Geobase.getGeobase().findOne(gid);
        return MapsArea.createMapsArea(region.getLongitude(), region.getLatitude(),
                region.getLongitudeSize(), region.getLatitudeSize());
    }
}
