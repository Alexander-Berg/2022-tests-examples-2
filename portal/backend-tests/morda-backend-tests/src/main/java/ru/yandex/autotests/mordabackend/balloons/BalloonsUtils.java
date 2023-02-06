package ru.yandex.autotests.mordabackend.balloons;

import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.HashMap;
import java.util.Map;

import static ru.yandex.autotests.utils.morda.region.Region.*;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: ivannik
 * Date: 29.09.2014
 */
public class BalloonsUtils {

    public static Map<Domain, String> NEAR_CAPITAL_REGION_IP = new HashMap<Domain, String>() {{
        put(RU, "217.174.104.48");
        put(UA, "5.207.164.163");
        put(KZ, "2.133.227.79");
        put(BY, "134.17.32.242");
        put(COM_TR, "213.153.249.33");
    }};

    public static Map<Domain, String> FAR_FROM_CAPITAL_REGION_IP = new HashMap<Domain, String>() {{
        put(RU, "213.21.63.173");
        put(UA, "213.21.63.173");
        put(KZ, "213.21.63.173");
        put(BY, "213.21.63.173");
        put(COM_TR, "78.135.73.172");
    }};

    public static Map<Domain, String> OTHER_CITY_IN_DOMAIN_IP = new HashMap<Domain, String>() {{
        put(RU, "80.70.231.6");
        put(UA, "178.137.165.233");
        put(KZ, "178.89.171.174");
        put(BY, "95.46.200.84");
        put(COM_TR, "188.3.190.7");
    }};

    public static Map<Domain, Region> OTHER_CITY_IN_DOMAIN_REGIONS = new HashMap<Domain, Region>() {{
        put(RU, SPB);
        put(UA, LVOV);
        put(KZ, KARAGANDA);
        put(BY, VITEBSK);
        put(COM_TR, ANTALYA);
    }};
}
