package ru.yandex.autotests.tunewebtests.retpath;

import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneapitests.utils.Region;

import java.util.HashMap;
import java.util.Map;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class RetpathData {
    public static final Map<Domain,Region> REGION_FOR_DOMAIN = new HashMap<Domain,Region>() {{
        put(Domain.RU, Region.SPB);
        put(Domain.KZ, Region.ALMATA);
        put(Domain.UA, Region.LVOV);
        put(Domain.BY, Region.BREST);
        put(Domain.COM, Region.SPB);
        put(Domain.COM_TR, Region.SPB);
    }};
}
