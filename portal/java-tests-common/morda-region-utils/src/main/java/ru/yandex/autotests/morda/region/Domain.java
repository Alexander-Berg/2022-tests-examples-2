package ru.yandex.autotests.morda.region;

import com.google.common.net.InternetDomainName;
import ru.yandex.qatools.geobase.GeobaseRegion;

import java.net.URI;
import java.util.List;

import static ru.yandex.autotests.morda.region.Region.BELARUS;
import static ru.yandex.autotests.morda.region.Region.KAZAKHSTAN;
import static ru.yandex.autotests.morda.region.Region.UKRAINE;
import static ru.yandex.qatools.geobase.GeobaseRegion.geobaseRegion;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/07/15
 */
public enum Domain {
    RU("ru"),
    UA("ua"),
    BY("by"),
    KZ("kz"),
    COM("com"),
    COM_TR("com.tr");

    private String value;

    Domain(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    public static Domain fromValue(String value) {
        for (Domain d : values()) {
            if (d.getValue().equals(value)) {
                return d;
            }
        }
        throw new IllegalArgumentException("Domain " + value + " not found");
    }

    public static Domain fromUri(URI uri) {
        String host = uri.getHost();
        if (host == null) {
            throw new RuntimeException("Host not found in URI \"" + uri + "\"");
        }
        InternetDomainName publicSuffix = InternetDomainName.from(host).publicSuffix();
        return fromValue(publicSuffix.toString());
    }

    public static Domain kubrDomain(int regionId) {
        return kubrDomain(geobaseRegion(regionId));
    }

    public static Domain kubrDomain(Region region) {
        return kubrDomain(region.getGeobaseRegion());
    }

    public static Domain kubrDomain(GeobaseRegion region) {
        List<Integer> parents = region.getParents();

        if (region.getId() == BELARUS.getId() || parents.contains(BELARUS.getId())) {
            return BY;
        } else if (region.getId() == UKRAINE.getId() || parents.contains(UKRAINE.getId())) {
            return UA;
        } else if (region.getId() == KAZAKHSTAN.getId() || parents.contains(KAZAKHSTAN.getId())) {
            return KZ;
        } else {
            return RU;
        }
    }

    @Override
    public String toString() {
        return value;
    }
}
