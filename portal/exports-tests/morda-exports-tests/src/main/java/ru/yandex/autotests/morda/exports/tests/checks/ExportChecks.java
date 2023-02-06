package ru.yandex.autotests.morda.exports.tests.checks;

import org.hamcrest.Matcher;
import org.hamcrest.collection.IsIn;
import ru.yandex.autotests.morda.exports.MordaExport;
import ru.yandex.autotests.morda.exports.geo.GeoEntry;
import ru.yandex.autotests.morda.exports.geo.GeoPanoramsExport;
import ru.yandex.autotests.morda.exports.geo.GeoRoutesExport;
import ru.yandex.autotests.morda.exports.maps.MapsEntry;
import ru.yandex.autotests.morda.exports.maps.MapsExport;
import ru.yandex.autotests.morda.exports.sign.SignAutoV2Export;
import ru.yandex.autotests.morda.exports.sign.SignAutoruV2Export;
import ru.yandex.autotests.morda.exports.sign.SignBrowserV2Export;
import ru.yandex.autotests.morda.exports.sign.SignEntry;
import ru.yandex.autotests.morda.exports.sign.SignMarketV2Export;
import ru.yandex.autotests.morda.exports.sign.SignMasterV2Export;
import ru.yandex.autotests.morda.exports.sign.SignMusicV2Export;
import ru.yandex.autotests.morda.exports.sign.SignRabotaV2Export;
import ru.yandex.autotests.morda.exports.sign.SignRealtyV2Export;
import ru.yandex.autotests.morda.exports.sign.SignTaxiV2Export;
import ru.yandex.autotests.morda.exports.sign.SignTravelV2Export;

import java.net.URI;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.isEmptyString;
import static org.hamcrest.Matchers.isOneOf;
import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.exports.tests.checks.HttpResponseCheck.httpResponse;
import static ru.yandex.autotests.morda.exports.tests.checks.MapsCoordsCheck.mapsCoords;
import static ru.yandex.autotests.morda.exports.tests.checks.RegionTargetingCheck.regionTargeting;
import static ru.yandex.autotests.morda.exports.tests.checks.RegionTranslationsCheck.regionTranslationsChek;
import static ru.yandex.autotests.morda.exports.tests.checks.UrlPatternCheck.urlPattern;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.ParamMatcher.urlParam;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.ParamMatcher.urlParamOrNull;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;

/**
 * User: asamar
 * Date: 13.08.2015.
 */
public class ExportChecks<T extends MordaExport<T, E>, E> {
    public static final List<String> LANGUAGES = Arrays.asList("ru", "ua", "by", "kz", "tt");
    public static final Matcher<Integer> TEXT_LENGTH_MATCHER = allOf(greaterThanOrEqualTo(1), lessThanOrEqualTo(22));

    public static final Function<SignEntry, Matcher<String>> SIGN_TAXI_URL_MATCHER = e -> urlMatcher()
            .scheme("https")
            .host("taxi.yandex.ru")
            .path("/")
            .urlParams(
                    urlParam("utm_content", isOneOf("spb", "msk", "tul", "ekb", "kln","soc","kra", "per", "kvk", "nsk",
                            "vkv","kzn","nno","vrn","rnd","che","tom","oms","min","ufa","sam")),
                    urlParam("utm_source", "yandex_service_list"),
                    urlParam("utm_term", startsWith(e.getCounter()))
            )
            .build();

    public static final Function<SignEntry, Matcher<String>> SIGN_BROWSER_URL_MATCHER = e -> urlMatcher()
            .scheme("https")
            .host(startsWith("browser.yandex."))
            .path("/")
            .urlParams(
                    urlParam("from", not(isEmptyOrNullString())),
                    urlParam("banerid", not(isEmptyOrNullString()))
            )
            .build();

    public static final Function<SignEntry, Matcher<String>> SIGN_MUSIC_URL_MATCHER = e -> urlMatcher()
            .scheme("https")
            .host(startsWith("music.yandex."))
            .path(startsWith("/"))
            .urlParams(
                    urlParam("utm_source", "yandex_service_list")
            )
            .build();

    private MordaExport<T, E> export;
    private List<ExportCheck<E>> checks;
    private List<ExportCheck<T>> exportCheck;

    @SafeVarargs
    private ExportChecks(MordaExport<T, E> export, List<ExportCheck<E>> checks, ExportCheck<T>... exportChecks) {
        this.export = export;
        this.checks = checks;
        this.exportCheck = asList(exportChecks);
    }

    public static ExportChecks<MapsExport, MapsEntry> getMapsChecks() {
        return new ExportChecks<MapsExport, MapsEntry>(
                new MapsExport(),
                asList(
                        httpResponse("url", MapsEntry::getUrl, e -> e.getUrl() != null),
                        httpResponse("narod", MapsEntry::getNarod, e -> e.getNarod() != null),
                        urlPattern(
                                "url",
                                MapsEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(anyOf(
                                                startsWith("maps.yandex."),
                                                equalTo("harita.yandex.com.tr")
                                        ))
                                        .path(matches("/(?:\\w+/)*"))
                                        .build(),
                                e -> e.getUrl() != null
                        ),
                        urlPattern(
                                "narod",
                                MapsEntry::getNarod,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("n.maps.yandex.ru")
                                        .path(matches("/(?:\\w+/)*"))
                                        .urlParams(
                                                urlParam("ll", not(isEmptyOrNullString()))
                                        )
                                        .build(),
                                e -> e.getNarod() != null
                        ),
                        mapsCoords(
                                "url",
                                MapsEntry::getUrl,
                                MapsEntry::getGeo,
                                e -> e.getUrl() != null && e.getUrl().contains("ll=")
                        ),
                        mapsCoords(
                                "narod",
                                MapsEntry::getNarod,
                                MapsEntry::getGeo,
                                e -> e.getNarod() != null && e.getNarod().contains("ll=")
                        )
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<GeoPanoramsExport, GeoEntry> getGeoPanoramsChecks() {
        return new ExportChecks<GeoPanoramsExport, GeoEntry>(
                new GeoPanoramsExport(),
                asList(
                        httpResponse("url", GeoEntry::getUrl),
                        urlPattern(
                                "url",
                                GeoEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("maps.yandex."))
                                        .path(not(isEmptyOrNullString()))
                                        .urlParams(
                                                urlParamOrNull("utm_source", endsWith(e.getCounter()))
                                        )
                                        .build()
                        ),
                        DomainCheck.domain("url", GeoEntry::getUrl, GeoEntry::getGeo),
                        mapsCoords(
                                "url",
                                GeoEntry::getUrl,
                                GeoEntry::getGeo,
                                e -> e.getUrl() != null && e.getGeo() != 10000
                        )
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<GeoRoutesExport, GeoEntry> getGeoRoutesChecks() {
        return new ExportChecks<GeoRoutesExport, GeoEntry>(
                new GeoRoutesExport(),
                Arrays.asList(
                        httpResponse("url", GeoEntry::getUrl),
                        urlPattern(
                                "url",
                                GeoEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("maps.yandex."))
                                        .path(notNullValue(String.class))
                                        .urlParams(
                                                urlParamOrNull("utm_source", e.getCounter())
                                        )
                                        .build()
                        ),
                        DomainCheck.domain("url", GeoEntry::getUrl, GeoEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<SignTaxiV2Export, SignEntry> getSignTaxiV2Checks() {
        return new ExportChecks<SignTaxiV2Export, SignEntry>(
                new SignTaxiV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                SIGN_TAXI_URL_MATCHER
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                SIGN_TAXI_URL_MATCHER
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<SignTravelV2Export, SignEntry> getSignTravelV2Checks() {
        return new ExportChecks<SignTravelV2Export, SignEntry>(
                new SignTravelV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("travel.yandex.ru")
                                        .path(IsIn.<String>isIn(asList("/search", "/")))
                                        .urlParams(
                                                urlParam("utm_campaign", "yandex"),
                                                urlParam("utm_source", "yandex_sign"),
                                                urlParam("utm_content", e.getCounter())
                                        )
                                        .build()
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("travel.yandex.ru")
                                        .path(IsIn.<String>isIn(asList("/search", "/")))
                                        .urlParams(
                                                urlParam("utm_campaign", "yandex"),
                                                urlParam("utm_source", "yandex_sign"),
                                                urlParam("utm_content", e.getCounter())
                                        )
                                        .build()
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<SignAutoV2Export, SignEntry> getSignAutoV2Checks() {
        return new ExportChecks<SignAutoV2Export, SignEntry>(
                new SignAutoV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("auto.yandex."))
                                        .path(startsWith("/"))
                                        .urlParams(
                                                urlParam("from", "morda"),
                                                urlParamOrNull("utm_source", "yandex_list_service"),
                                                urlParamOrNull("utm_content", e.getCounter()),
                                                urlParamOrNull("_openstat", allOf(
                                                        containsString("title"),
                                                        containsString(e.getCounter())
                                                ))
                                        )
                                        .build()
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme(isOneOf("https", null))
                                        .host(anyOf(
                                                startsWith("auto.yandex."),
                                                startsWith("www.yandex.")
                                        ))
                                        .path(startsWith("/"))
                                        .urlParams(
                                                urlParam("from", "morda"),
                                                urlParamOrNull("utm_source", "yandex_list_service"),
                                                urlParamOrNull("utm_content", e.getCounter()),
                                                urlParamOrNull("_openstat", allOf(
                                                        containsString("text"),
                                                        containsString(e.getCounter())
                                                ))
                                        )
                                        .build()
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<SignAutoruV2Export, SignEntry> getSignAutoruV2Checks() {
        return new ExportChecks<SignAutoruV2Export, SignEntry>(
                new SignAutoruV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext)
//                        urlPattern(
//                                "url",
//                                SignEntry::getUrl,
//                                e -> urlMatcher()
//                                        .scheme("http")
//                                        .host(IsIn.<String>isIn(asList("auto.ru", "my.auto.ru")))
//                                        .path(startsWith("/"))
//                                        .urlParams(
//                                                urlParam("from", "morda"),
//                                                urlParam("utm_source", "yandex_list_service"),
//                                                urlParam("utm_content", e.getCounter())
//                                        )
//                                        .build()
//                        ),
//                        urlPattern(
//                                "urlText",
//                                SignEntry::getUrltext,
//                                e -> urlMatcher()
//                                        .scheme("http")
//                                        .host(IsIn.<String>isIn(asList("auto.ru", "my.auto.ru")))
//                                        .path(startsWith("/"))
//                                        .urlParams(
//                                                urlParam("from", "morda"),
//                                                urlParam("utm_source", "yandex_list_service"),
//                                                urlParam("utm_content", e.getCounter())
//                                        )
//                                        .build()
//                        ),
//                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
//                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
//                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
//                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                )
//                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static final ExportChecks<SignBrowserV2Export, SignEntry> getSignBrowserV2Checks() {
        return new ExportChecks<SignBrowserV2Export, SignEntry>(
                new SignBrowserV2Export(),
                asList(
                        httpResponse("url", e -> e.getUrl().replace("|", "%7C")),
                        httpResponse("urlText", e -> e.getUrltext().replace("|", "%7C")),
                        urlPattern(
                                "url",
                                e -> e.getUrl().replace("|", "%7C"),
                                SIGN_BROWSER_URL_MATCHER
                        ),
                        urlPattern(
                                "urlText",
                                e -> e.getUrltext().replace("|", "%7C"),
                                SIGN_BROWSER_URL_MATCHER
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<SignMarketV2Export, SignEntry> getSignMarketV2Checks() {
        return new ExportChecks<SignMarketV2Export, SignEntry>(
                new SignMarketV2Export(),
                asList(
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("market.yandex."))
                                        .path(not(isEmptyString()))
                                        .build()
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<SignMasterV2Export, SignEntry> getSignMasterV2Checks() {
        return new ExportChecks<SignMasterV2Export, SignEntry>(
                new SignMasterV2Export(),
                asList(
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("master.yandex.ru")
                                        .path("/")
                                        .urlParams(
                                                urlParam("utm_source", "face"),
                                                urlParam("region_id", String.valueOf(e.getGeo()))
                                        )
                                        .build()
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<SignMusicV2Export, SignEntry> getSignMusicV2Checks() {
        return new ExportChecks<SignMusicV2Export, SignEntry>(
                new SignMusicV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                SIGN_MUSIC_URL_MATCHER
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                SIGN_MUSIC_URL_MATCHER
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static final ExportChecks<SignRabotaV2Export, SignEntry> getSignRabotaV2Checks() {
        return new ExportChecks<SignRabotaV2Export, SignEntry>(
                new SignRabotaV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("rabota.yandex."))
                                        .path(not(isEmptyOrNullString()))
                                        .urlParams(
                                                urlParam("from", "morda"),
                                                urlParam("_openstat", allOf(
                                                        containsString(e.getCounter()),
                                                        containsString("title")
                                                ))

                                        )
                                        .build()),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(anyOf(
                                                startsWith("rabota.yandex."),
                                                startsWith("mobile.yandex.")
                                        ))
                                        .path(not(isEmptyOrNullString()))
                                        .urlParams(
                                                urlParam("from", equalTo("morda")),
                                                urlParam("_openstat", allOf(
                                                        containsString(e.getCounter()),
                                                        containsString("text")
                                                ))

                                        )
                                        .build()),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public static ExportChecks<SignRealtyV2Export, SignEntry> getSignRealtyV2Checks() {
        return new ExportChecks<SignRealtyV2Export, SignEntry>(
                new SignRealtyV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("realty.yandex."))
                                        .path(not(isEmptyOrNullString()))
                                        .urlParams(
                                                urlParamOrNull("utm_source", "yandex_sign"),
                                                urlParamOrNull("_openstat", endsWith(e.getCounter())),
                                                urlParamOrNull("utm_content", e.getCounter())
                                        )
                                        .build()
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("realty.yandex."))
                                        .path(not(isEmptyOrNullString()))
                                        .urlParams(
                                                urlParamOrNull("utm_source", "yandex_sign"),
                                                urlParamOrNull("_openstat", endsWith(e.getCounter())),
                                                urlParamOrNull("utm_content", e.getCounter())
                                        )
                                        .build()
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", LANGUAGES)
        );
    }

    public Collection<Object[]> getChecks(URI mordaHost, boolean needPings) {
        export.populate(mordaHost);
        if (!needPings) {
                checks = checks.stream()
                        .filter(e -> !(e instanceof HttpResponseCheck))
                        .collect(Collectors.toList());
        }

        List<Object[]> data = new ArrayList<>();
        for (E entry : export.getData()) {
            for (ExportCheck<E> check : checks) {
                if (check.getCondition().test(entry)) {
                    data.add(new Object[]{export.getName(), entry, check});
                }
            }
        }
        exportCheck.forEach(e -> data.add(new Object[]{export.getName(), export, e}));
        return data;
    }

    public MordaExport<T, E> getExport() {
        return export;
    }

    public List<ExportCheck<E>> getChecks() {
        return checks;
    }
}
