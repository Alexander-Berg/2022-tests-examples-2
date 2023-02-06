package ru.yandex.autotests.metrika.appmetrica.data;

import static ru.yandex.autotests.metrika.appmetrica.data.Partner.NAME;

/**
 * Created by graev on 01/12/2016.
 */
public class Partners {

    public static final Partner ORGANIC = new Partner(0L)
            .put(NAME, "Organic");

    public static final Partner ZORKA = new Partner(42L)
            .put(NAME, "Zorka");

    public static final Partner PORTAL = new Partner(254L)
            .put(NAME, "Portal");

    public static final Partner ADWORDS = new Partner(30101L)
            .put(NAME, "AdWords");

    public static final Partner FACEBOOK = new Partner(5L)
            .put(NAME, "Facebook");

    public static final Partner MYTARGET = new Partner(136L)
            .put(NAME, "MyTarget");

    public static final Partner DIRECT = new Partner(43L)
            .put(NAME, "Direct");

    public static final Partner DOUBLECLICK = new Partner(69648L)
            .put(NAME, "DoubleClick");

    public static final Partner EXPERIMENTS = new Partner(410L)
            .put(NAME, "Эксперименты");

    public static final Partner TIKTOK = new Partner(85825L)
            .put(NAME, "TikTok");

    public static final Partner HUAWEI_ADS = new Partner(122101L)
            .put(NAME, "Huawei Ads");
}
