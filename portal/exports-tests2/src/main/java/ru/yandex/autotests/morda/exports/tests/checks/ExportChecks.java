package ru.yandex.autotests.morda.exports.tests.checks;

import org.hamcrest.Matcher;
import org.hamcrest.collection.IsIn;
import ru.yandex.autotests.morda.exports.MordaExport;
import ru.yandex.autotests.morda.exports.MordaExportEntry;
import ru.yandex.autotests.morda.exports.geo.GeoEntry;
import ru.yandex.autotests.morda.exports.geo.GeoPanoramsExport;
import ru.yandex.autotests.morda.exports.geo.GeoRoutesExport;
import ru.yandex.autotests.morda.exports.maps.MapsEntry;
import ru.yandex.autotests.morda.exports.maps.MapsExport;
import ru.yandex.autotests.morda.exports.sign.SignAutoExport;
import ru.yandex.autotests.morda.exports.sign.SignAutoruExport;
import ru.yandex.autotests.morda.exports.sign.SignBrowserExport;
import ru.yandex.autotests.morda.exports.sign.SignEntry;
import ru.yandex.autotests.morda.exports.sign.SignMarketExport;
import ru.yandex.autotests.morda.exports.sign.SignMasterExport;
import ru.yandex.autotests.morda.exports.sign.SignMusicExport;
import ru.yandex.autotests.morda.exports.sign.SignRabotaExport;
import ru.yandex.autotests.morda.exports.sign.SignRealtyExport;
import ru.yandex.autotests.morda.exports.sign.SignTaxiExport;
import ru.yandex.autotests.morda.exports.sign.SignTravelExport;

import java.net.URI;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.function.Function;

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
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.morda.exports.tests.checks.HttpResponseCheck.httpResponse;
import static ru.yandex.autotests.morda.exports.tests.checks.MapsCoordsCheck.mapsCoords;
import static ru.yandex.autotests.morda.exports.tests.checks.RegionTargetingCheck.regionTargeting;
import static ru.yandex.autotests.morda.exports.tests.checks.RegionTranslationsCheck.regionTranslationsChek;
import static ru.yandex.autotests.morda.exports.tests.checks.UrlPatternCheck.urlPattern;
import static ru.yandex.autotests.morda.exports.tests.utils.UrlMatcher.ParamMatcher.urlParam;
import static ru.yandex.autotests.morda.exports.tests.utils.UrlMatcher.urlMatcher;

/**
 * User: asamar
 * Date: 13.08.2015.
 */
public class ExportChecks<T extends MordaExport<T, E>, E extends MordaExportEntry> {
    private static final List<String> LANGUAGES = Arrays.asList("ru", "ua", "by", "kz", "tt");
    private static final Matcher<Integer> TEXT_LENGTH_MATCHER = allOf(greaterThanOrEqualTo(1), lessThanOrEqualTo(22));

    public static final ExportChecks MAPS_CHECKS = new ExportChecks<>(
            new MapsExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", MapsEntry::getUrl, e -> e.getUrl() != null),
                    HttpResponseCheck.httpResponse("narod", MapsEntry::getNarod, e -> e.getNarod() != null),
                    UrlPatternCheck.urlPattern(
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
                    UrlPatternCheck.urlPattern(
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

    public static final ExportChecks GEO_PANORAMS_CHECKS = new ExportChecks<>(
            new GeoPanoramsExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", GeoEntry::getUrl),
                    UrlPatternCheck.urlPattern(
                            "url",
                            GeoEntry::getUrl,
                            e -> urlMatcher()
                                    .scheme("https")
                                    .host(startsWith("maps.yandex."))
                                    .path(not(isEmptyOrNullString()))
                                    .urlParams(
                                            urlParam("utm_source", anyOf(
                                                    endsWith(e.getCounter()),
                                                    isEmptyOrNullString()
                                            ))
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

    public static final ExportChecks GEO_ROUTES_CHECK = new ExportChecks<>(
            new GeoRoutesExport(),
            Arrays.asList(
                    HttpResponseCheck.httpResponse("url", GeoEntry::getUrl),
                    UrlPatternCheck.urlPattern(
                            "url",
                            GeoEntry::getUrl,
                            e -> urlMatcher()
                                    .scheme("https")
                                    .host(startsWith("maps.yandex."))
                                    .path(notNullValue(String.class))
                                    .urlParams(
                                            urlParam("utm_source", anyOf(
                                                            equalTo(e.getCounter()),
                                                            isEmptyOrNullString())
                                            )
                                    )
                                    .build()
                    ),
                    DomainCheck.domain("url", GeoEntry::getUrl, GeoEntry::getGeo)
            ),
            regionTranslationsChek("geo", LANGUAGES)
    );

    public static final Function<SignEntry, Matcher<String>> SIGN_TAXI_URL_MATCHER = e -> urlMatcher()
            .scheme("https")
            .host("taxi.yandex.ru")
            .path("/")
            .urlParams(
                    urlParam("utm_content", isOneOf("spb", "msk", "tul", "ekb")),
                    urlParam("utm_source", "yandex_service_list"),
                    urlParam("utm_term", startsWith(e.getCounter()))
            )
            .build();

    public static final ExportChecks SIGN_TAXI_CHECK = new ExportChecks<>(
            new SignTaxiExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", SignEntry::getUrl),
                    HttpResponseCheck.httpResponse("urlText", SignEntry::getUrltext),
                    UrlPatternCheck.urlPattern(
                            "url",
                            SignEntry::getUrl,
                            SIGN_TAXI_URL_MATCHER
                    ),
                    UrlPatternCheck.urlPattern(
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

    public static final ExportChecks SIGN_TRAVEL_CHECKS = new ExportChecks<>(
            new SignTravelExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", SignEntry::getUrl),
                    HttpResponseCheck.httpResponse("urlText", SignEntry::getUrltext),
                    UrlPatternCheck.urlPattern(
                            "url",
                            SignEntry::getUrl,
                            e -> urlMatcher()
                                    .scheme("https")
                                    .host("travel.yandex.ru")
                                    .path("/")
                                    .urlParams(
                                            urlParam("from", "morda"),
                                            urlParam("utm_campaign", "yandex"),
                                            urlParam("utm_source", "yandex_sign"),
                                            urlParam("utm_content", e.getCounter())
                                    )
                                    .build()
                    ),
                    UrlPatternCheck.urlPattern(
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

    public static final ExportChecks SIGN_AUTO_CHECKS = new ExportChecks<>(
            new SignAutoExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", SignEntry::getUrl),
                    HttpResponseCheck.httpResponse("urlText", SignEntry::getUrltext),
                    UrlPatternCheck.urlPattern(
                            "url",
                            SignEntry::getUrl,
                            e -> urlMatcher()
                                    .scheme("https")
                                    .host(startsWith("auto.yandex."))
                                    .path("/")
                                    .urlParams(
                                            urlParam("from", "morda"),
                                            urlParam("utm_source", anyOf(
                                                    equalTo("yandex_list_service"),
                                                    isEmptyOrNullString()
                                            )),
                                            urlParam("utm_content", anyOf(
                                                    equalTo(e.getCounter()),
                                                    isEmptyOrNullString()
                                            )),
                                            urlParam("_openstat", anyOf(
                                                    allOf(
                                                            containsString("title"),
                                                            containsString(e.getCounter())
                                                    ),
                                                    isEmptyOrNullString()
                                            ))
                                    )
                                    .build()
                    ),
                    UrlPatternCheck.urlPattern(
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
                                            urlParam("utm_source", anyOf(
                                                    equalTo("yandex_list_service"),
                                                    isEmptyOrNullString()
                                            )),
                                            urlParam("utm_content", anyOf(
                                                    equalTo(e.getCounter()),
                                                    isEmptyOrNullString()
                                            )),
                                            urlParam("_openstat", anyOf(
                                                    allOf(
                                                            containsString("text"),
                                                            containsString(e.getCounter())
                                                    ),
                                                    isEmptyOrNullString()
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

    public static final ExportChecks SIGN_AUTORU_CHECKS = new ExportChecks<>(
            new SignAutoruExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", SignEntry::getUrl),
                    HttpResponseCheck.httpResponse("urlText", SignEntry::getUrltext),
                    UrlPatternCheck.urlPattern(
                            "url",
                            SignEntry::getUrl,
                            e -> urlMatcher()
                                    .scheme("http")
                                    .host("auto.ru")
                                    .path("/")
                                    .urlParams(
                                            urlParam("from", "morda"),
                                            urlParam("utm_source", "yandex_list_service"),
                                            urlParam("utm_content", e.getCounter())
                                    )
                                    .build()
                    ),
                    UrlPatternCheck.urlPattern(
                            "urlText",
                            SignEntry::getUrltext,
                            e -> urlMatcher()
                                    .scheme("http")
                                    .host(IsIn.<String>isIn(asList("auto.ru", "my.auto.ru")))
                                    .path(startsWith("/"))
                                    .urlParams(
                                            urlParam("from", "morda"),
                                            urlParam("utm_source", "yandex_list_service"),
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

    public static final Function<SignEntry, Matcher<String>> SIGN_BROWSER_URL_MATCHER = e -> urlMatcher()
            .scheme(isEmptyOrNullString())
            .host(startsWith("browser.yandex."))
            .path("/")
            .urlParams(
                    urlParam("from", not(isEmptyOrNullString())),
                    urlParam("banerid", not(isEmptyOrNullString()))
            )
            .build();

    public static final ExportChecks SIGN_BROWSER_CHECKS = new ExportChecks<>(
            new SignBrowserExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", e -> e.getUrl().replace("|", "%7C")),
                    HttpResponseCheck.httpResponse("urlText", e -> e.getUrltext().replace("|", "%7C")),
                    UrlPatternCheck.urlPattern(
                            "url",
                            SignEntry::getUrl,
                            SIGN_BROWSER_URL_MATCHER
                    ),
                    UrlPatternCheck.urlPattern(
                            "urlText",
                            SignEntry::getUrltext,
                            SIGN_BROWSER_URL_MATCHER
                    ),
                    TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                    DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                    DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                    regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
            ),
            regionTranslationsChek("geo", LANGUAGES)
    );

    public static final ExportChecks SIGN_MARKET_CHECKS = new ExportChecks<>(
            new SignMarketExport(),
            asList(
                    HttpResponseCheck.httpResponse("urlText", SignEntry::getUrltext),
                    UrlPatternCheck.urlPattern(
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

    public static final ExportChecks SIGN_MASTER_CHECKS = new ExportChecks<>(
            new SignMasterExport(),
            asList(
                    HttpResponseCheck.httpResponse("urlText", SignEntry::getUrltext),
                    UrlPatternCheck.urlPattern(
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

    public static final Function<SignEntry, Matcher<String>> SIGN_MUSIC_URL_MATCHER = e -> urlMatcher()
            .scheme("https")
            .host(startsWith("music.yandex."))
            .path(startsWith("/"))
            .urlParams(
                    urlParam("utm_source", "yandex_service_list")
            )
            .build();

    public static final ExportChecks SIGN_MUSIC_CHECKS = new ExportChecks<>(
            new SignMusicExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", SignEntry::getUrl),
                    HttpResponseCheck.httpResponse("urlText", SignEntry::getUrltext),
                    UrlPatternCheck.urlPattern(
                            "url",
                            SignEntry::getUrl,
                            SIGN_MUSIC_URL_MATCHER
                    ),
                    UrlPatternCheck.urlPattern(
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

    public static final ExportChecks SIGN_RABOTA_CHECKS = new ExportChecks<>(
            new SignRabotaExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", SignEntry::getUrl),
                    HttpResponseCheck.httpResponse("urlText", SignEntry::getUrltext),
                    UrlPatternCheck.urlPattern(
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
                    UrlPatternCheck.urlPattern(
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

    public static final ExportChecks SIGN_REALTY_CHECKS = new ExportChecks<>(
            new SignRealtyExport(),
            asList(
                    HttpResponseCheck.httpResponse("url", SignEntry::getUrl),
                    HttpResponseCheck.httpResponse("urlText", SignEntry::getUrltext),
                    UrlPatternCheck.urlPattern(
                            "url",
                            SignEntry::getUrl,
                            e -> urlMatcher()
                                    .scheme("https")
                                    .host(startsWith("realty.yandex."))
                                    .path(not(isEmptyOrNullString()))
                                    .urlParams(
                                            urlParam("from", "morda"),
                                            urlParam("utm_source", anyOf(
                                                    equalTo("yandex_sign"),
                                                    isEmptyOrNullString()
                                            )),
                                            urlParam("_openstat", anyOf(
                                                    allOf(
                                                            containsString(e.getCounter()),
                                                            containsString("title")
                                                    ),
                                                    isEmptyOrNullString()
                                            )),
                                            urlParam("utm_content", anyOf(
                                                    equalTo(e.getCounter()),
                                                    isEmptyOrNullString()
                                            ))
                                    )
                                    .build()
                    ),
                    UrlPatternCheck.urlPattern(
                            "urlText",
                            SignEntry::getUrltext,
                            e -> urlMatcher()
                                    .scheme("https")
                                    .host(startsWith("realty.yandex."))
                                    .path(not(isEmptyOrNullString()))
                                    .urlParams(
                                            urlParam("from", "morda"),
                                            urlParam("utm_source", anyOf(
                                                    equalTo("yandex_sign"),
                                                    isEmptyOrNullString()
                                            )),
                                            urlParam("_openstat", anyOf(
                                                    allOf(
                                                            containsString(e.getCounter()),
                                                            containsString("text")
                                                    ),
                                                    isEmptyOrNullString()
                                            )),
                                            urlParam("utm_content", anyOf(
                                                    equalTo(e.getCounter()),
                                                    isEmptyOrNullString()
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

    private MordaExport<T, E> export;
    private List<ExportCheck<E>> checks;
    private List<ExportCheck<T>> exportCheck;

    @SafeVarargs
    private ExportChecks(MordaExport<T, E> export, List<ExportCheck<E>> checks, ExportCheck<T>... exportChecks) {
        this.export = export;
        this.checks = checks;
        this.exportCheck = asList(exportChecks);
    }

    public Collection<Object[]> getChecks(URI mordaHost) {
        export.populate(mordaHost);

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
