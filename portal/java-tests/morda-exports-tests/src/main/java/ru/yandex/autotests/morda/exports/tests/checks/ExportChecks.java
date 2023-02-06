package ru.yandex.autotests.morda.exports.tests.checks;

import org.hamcrest.Matcher;
import org.hamcrest.collection.IsIn;
import ru.yandex.autotests.morda.beans.exports.geo.GeoEntry;
import ru.yandex.autotests.morda.beans.exports.geo.GeoPanoramsExport;
import ru.yandex.autotests.morda.beans.exports.geo.GeoRoutesExport;
import ru.yandex.autotests.morda.beans.exports.maps.MapsEntry;
import ru.yandex.autotests.morda.beans.exports.maps.MapsExport;
import ru.yandex.autotests.morda.beans.exports.sign.SignAutoV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignAutoruTouchV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignAutoruV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignAviaV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignBrowserV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignEntry;
import ru.yandex.autotests.morda.beans.exports.sign.SignImagesV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignKinopoiskOldV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignKinopoiskV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignMarketTouchV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignMarketV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignMasterV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignMoneyV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignMusicV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignRabotaTouchV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignRabotaV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignRadioV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignRealtyTouchV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignRealtyV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignSearchV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignTaxiTouchV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignTaxiV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignTravelTouchV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignTravelV2Export;
import ru.yandex.autotests.morda.beans.exports.sign.SignVideoV2Export;
import ru.yandex.autotests.morda.exports.AbstractMordaExport;
import ru.yandex.autotests.morda.exports.interfaces.Entry;
import ru.yandex.autotests.morda.pages.MordaLanguage;

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
import static ru.yandex.autotests.morda.matchers.string.RegexMatcher.regex;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.morda.matchers.url.UrlQueryMatcher.queryMatcher;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;

/**
 * User: asamar
 * Date: 13.08.2015.
 */
public class ExportChecks<T extends AbstractMordaExport<T, E>, E extends Entry> {
    //    public static final List<String> LANGUAGES = Arrays.asList("ru", "ua", "by", "kz");
    public static final List<MordaLanguage> MORDA_LANGUAGES = Arrays.asList(RU, UK, BE, KK);
    public static final Matcher<Integer> TEXT_LENGTH_MATCHER = allOf(greaterThanOrEqualTo(1), lessThanOrEqualTo(22));

    public static final Function<SignEntry, Matcher<String>> SIGN_TAXI_URL_MATCHER = e -> urlMatcher()
            .scheme("https")
            .host(startsWith("taxi.yandex."))
            .path("/")
            .query(queryMatcher(true)
                    .param("utm_content", not(isEmptyOrNullString()))
                    .param("utm_source", "yandex-service-list")
                    .param("utm_term", not(isEmptyOrNullString()))
            );

    public static final Function<SignEntry, Matcher<String>> SIGN_BROWSER_URL_MATCHER = e -> urlMatcher()
            .scheme("https")
            .host(startsWith("browser.yandex."))
            .path(startsWith("/"))
            .query(queryMatcher(true)
                    .param("from", not(isEmptyOrNullString()))
                    .paramOrNull("banerid", not(isEmptyOrNullString()))
            );

    public static final Function<SignEntry, Matcher<String>> SIGN_MUSIC_URL_MATCHER = e -> urlMatcher()
            .scheme("https")
            .host(startsWith("music.yandex."))
            .path("/")
            .query(queryMatcher(true)
                    .param("utm_source", "yandex_service_list")
            );

    private AbstractMordaExport<T, E> export;
    private List<ExportCheck<E>> checks;
    private List<ExportCheck<T>> exportCheck;

    @SafeVarargs
    private ExportChecks(AbstractMordaExport<T, E> export, List<ExportCheck<E>> checks, ExportCheck<T>... exportChecks) {
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
                                                startsWith("yandex."),
                                                equalTo("yandex.com.tr")
                                        ))
                                        .path(anyOf(
                                                startsWith("maps"),
                                                startsWith("harita")
                                        )),
                                e -> e.getUrl() != null
                        ),
                        urlPattern(
                                "narod",
                                MapsEntry::getNarod,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("n.maps.yandex.ru")
                                        .path(regex("/(?:\\w+/)*"))
                                        .query(queryMatcher(true)
                                                .param("ll", not(isEmptyOrNullString()))
                                        ),
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
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
                                        .host(startsWith("yandex."))
                                        .path(startsWith("maps"))
                                        .query(queryMatcher(true)
                                                .paramOrNull("utm_source", endsWith(e.getCounter()))
                                        )
                        ),
                        DomainCheck.domain("url", GeoEntry::getUrl, GeoEntry::getGeo),
                        mapsCoords(
                                "url",
                                GeoEntry::getUrl,
                                GeoEntry::getGeo,
                                e -> e.getUrl() != null && !e.getGeo().matches(10000)
                        )
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
                                        .query(queryMatcher(true)
                                                .paramOrNull("utm_source", e.getCounter())
                                        )
                        ),
                        DomainCheck.domain("url", GeoEntry::getUrl, GeoEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
                                        .path("/")
                                        .query(queryMatcher(true)
                                                .param("utm_campaign", "yandex")
                                                .param("utm_source", "yandex_sign")
                                                .param("utm_content", e.getCounter())
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("travel.yandex.ru")
                                        .path(IsIn.<String>isIn(asList("/search", "/")))
                                        .query(queryMatcher(true)
                                                .param("utm_campaign", "yandex")
                                                .param("utm_source", "yandex_sign")
                                                .param("utm_content", e.getCounter())
                                        )
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
                                        .query(queryMatcher(true)
                                                .param("from", "morda")
                                                .paramOrNull("utm_source", "yandex_list_service")
                                                .paramOrNull("utm_content", e.getCounter())
                                                .paramOrNull("_openstat", allOf(
                                                        containsString("title"),
                                                        containsString(e.getCounter())
                                                ))
                                        )
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
                                        .query(queryMatcher(true)
                                                .param("from", "morda")
                                                .paramOrNull("utm_source", "yandex_list_service")
                                                .paramOrNull("utm_content", e.getCounter())
                                                .paramOrNull("_openstat", allOf(
                                                        containsString("text"),
                                                        containsString(e.getCounter())
                                                ))
                                        )
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignAutoruV2Export, SignEntry> getSignAutoruV2Checks() {
        return new ExportChecks<SignAutoruV2Export, SignEntry>(
                new SignAutoruV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(containsString("auto.ru"))
                                        .path("/")
                                        .query(queryMatcher(true)
                                                .param("from", "morda")
                                                .param("utm_source", "yandex_list_service")
                                                .param("utm_content", startsWith(e.getCounter()))
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(IsIn.<String>isIn(asList("auto.ru", "my.auto.ru", "moscow.auto.ru")))
                                        .path(startsWith("/"))
                                        .query(queryMatcher(true)
                                                .param("from", "morda")
                                                .param("utm_source", "yandex_list_service")
                                                .param("utm_content", startsWith(e.getCounter()))
                                        )
                        )
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
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignMarketV2Export, SignEntry> getSignMarketV2Checks() {
        return new ExportChecks<SignMarketV2Export, SignEntry>(
                new SignMarketV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("market.yandex."))
                                        .path("/")
                                        .query(queryMatcher(true)
                                                .paramOrNull("clid", "568")
                                                .paramOrNull("utm_source", "face_title")
                                                .paramOrNull("utm_medium", not(isEmptyOrNullString()))
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("market.yandex."))
                                        .path(not(isEmptyOrNullString()))
                                        .query(queryMatcher(true)
                                                .paramOrNull("utm_source", not(isEmptyOrNullString()))
                                                .paramOrNull("utm_medium", not(isEmptyOrNullString()))
                                                .paramOrNull("utm_term", not(isEmptyOrNullString()))
                                        )
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignMarketTouchV2Export, SignEntry> getSignMarketTouchV2Checks() {
        return new ExportChecks<SignMarketTouchV2Export, SignEntry>(
                new SignMarketTouchV2Export(),
                asList(
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("m.market.yandex."))
                                        .path("/")
                                        .query(queryMatcher(true)
                                                .paramOrNull("clid", "569")
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("m.market.yandex."))
                                        .path(not(isEmptyOrNullString()))
                                        .query(queryMatcher(true)
                                                .paramOrNull("utm_source", not(isEmptyOrNullString()))
                                                .paramOrNull("utm_medium", not(isEmptyOrNullString()))
                                                .paramOrNull("utm_term", not(isEmptyOrNullString()))
                                        )
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
                                        .query(queryMatcher(true)
                                                .param("utm_source", "face")
                                                .param("region_id", String.valueOf(e.getGeo().getRegion().getRegionId()))
                                        )
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
                                e -> urlMatcher()
                                .scheme("https")
                                .host(startsWith("music.yandex."))
                                .path(not(isEmptyOrNullString()))
                                .query(queryMatcher(true)
                                        .param("utm_source", "yandex_service_list")
                                )
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
                                        .path("/")
                                        .query(queryMatcher(true)
                                                .param("from", "morda")
                                                .paramOrNull("_openstat", not(isEmptyOrNullString()))
                                                .paramOrNull("utm_content", startsWith(e.getCounter()))


                                        )
                        ),
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
                                        .query(queryMatcher(true)
                                                .param("from", equalTo("morda"))
                                                .paramOrNull("_openstat", not(isEmptyOrNullString()))
                                                .paramOrNull("utm_content", e.getCounter())


                                        )
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
                                        .path("/")
                                        .query(queryMatcher(true)
                                                .paramOrNull("utm_source", "yandex_sign")
                                                .paramOrNull("_openstat", not(isEmptyOrNullString()))
                                                .paramOrNull("utm_content", startsWith(e.getCounter()))
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("realty.yandex."))
                                        .path(not(isEmptyOrNullString()))
                                        .query(queryMatcher(true)
                                                .paramOrNull("utm_source", "yandex_sign")
                                                .paramOrNull("_openstat", not(isEmptyOrNullString()))
                                                .paramOrNull("utm_content", startsWith(e.getCounter()))
                                        )
                        ),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignAutoruTouchV2Export, SignEntry> getSignAutoruTouchV2Checks() {
        return new ExportChecks<SignAutoruTouchV2Export, SignEntry>(
                new SignAutoruTouchV2Export(),
                asList(
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .path("/")
                                        .host(containsString("auto.ru"))
                                        .query(queryMatcher(true)
                                                .param("utm_content", e.getCounter())
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(containsString("auto.ru"))
                                        .query(queryMatcher(true)
                                                .param("utm_content", e.getCounter())
                                        )
                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo)
//                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                )
        );
    }

    public static ExportChecks<SignAviaV2Export, SignEntry> getSignAviaV2Checks() {
        return new ExportChecks<SignAviaV2Export, SignEntry>(
                new SignAviaV2Export(),
                asList(
                        urlPattern(
                                "url",
                                e -> e.getUrl().replace("|", "%7C"),
                                e -> urlMatcher()
                                        .scheme("https")
                                        .path("/")
                                        .host(startsWith("avia.yandex."))
                                        .query(queryMatcher(true)
                                                        .param("utm_source", "yamain")
//                                                .param("utm_campaign", e.getCounter().replace("avia_",""))
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                e -> e.getUrltext().replace("|", "%7C"),
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("avia.yandex."))
                                        .query(queryMatcher(true)
                                                        .param("utm_source", "yamain")
//                                                .param("utm_campaign", e.getCounter().replace("avia_",""))
                                        )
                        ),
                        httpResponse("url", e -> e.getUrl().replace("|", "%7C")),
                        httpResponse("urlText", e -> e.getUrltext().replace("|", "%7C")),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignImagesV2Export, SignEntry> getSignImagesV2Checks() {
        return new ExportChecks<SignImagesV2Export, SignEntry>(
                new SignImagesV2Export(),
                asList(
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("yandex."))
                                        .path(containsString("images"))
                                        .query(queryMatcher(true)
                                                .param("source", e.getCounter())
                                                .param("text", not(isEmptyOrNullString()))
                                        )

                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignKinopoiskV2Export, SignEntry> getSignKinopoiskV2Checks() {
        return new ExportChecks<SignKinopoiskV2Export, SignEntry>(
                new SignKinopoiskV2Export(),
                asList(
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .host(containsString("kinopoisk.ru"))
                                        .query(queryMatcher(true)
                                                .param("utm_source", "yamain")
                                                .param("utm_content", e.getCounter())
                                        )
                        ),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignKinopoiskOldV2Export, SignEntry> getSignKinopoiskOldV2Checks() {
        return new ExportChecks<SignKinopoiskOldV2Export, SignEntry>(
                new SignKinopoiskOldV2Export(),
                asList(
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .host(containsString("kinopoisk.ru"))
                                        .query(queryMatcher(true)
                                                .param("utm_source", "yamain")
                                                .param("utm_content", e.getCounter())
                                        )

                        ),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignMoneyV2Export, SignEntry> getSignMoneyV2Checks() {
        return new ExportChecks<SignMoneyV2Export, SignEntry>(
                new SignMoneyV2Export(),
                asList(
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("money.yandex.ru")
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("http")
                                        .host("money.yandex.ru")
                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignRabotaTouchV2Export, SignEntry> getSignRabotaTouchV2Checks() {
        return new ExportChecks<SignRabotaTouchV2Export, SignEntry>(
                new SignRabotaTouchV2Export(),
                asList(
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("m.rabota.yandex."))
                                        .path("/")
                                        .query(queryMatcher(true)
                                                .param("utm_content", startsWith(e.getCounter()))
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("m.rabota.yandex."))
                                        .query(queryMatcher(true)
                                                .param("utm_content", e.getCounter())
                                        )
                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo)
//                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                )
        );
    }

    public static ExportChecks<SignRadioV2Export, SignEntry> getSignRadioV2Checks() {
        return new ExportChecks<SignRadioV2Export, SignEntry>(
                new SignRadioV2Export(),
                asList(
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("radio.yandex.ru")
                                        .query(queryMatcher(true)
                                                .param("utm_campaign", e.getCounter())
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("radio.yandex.ru")
                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignRealtyTouchV2Export, SignEntry> getSignRealtyTouchV2Checks() {
        return new ExportChecks<SignRealtyTouchV2Export, SignEntry>(
                new SignRealtyTouchV2Export(),
                asList(
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("realty.yandex."))
                                        .path("/")
                                        .query(queryMatcher(true)
//                                                .param("utm_content", e.getCounter())
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("realty.yandex."))
                                        .query(queryMatcher(true)
//                                                .param("utm_content",e.getCounter())
                                        )
                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo)
//                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                )
        );
    }

    public static ExportChecks<SignSearchV2Export, SignEntry> getSignSearchV2Checks() {
        return new ExportChecks<SignSearchV2Export, SignEntry>(
                new SignSearchV2Export(),
                asList(
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("yandex." + e.getDomain()))
                                        .path("/search/")
                                        .query(queryMatcher(true)
                                                .param("text", not(isEmptyOrNullString()))
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("yandex." + e.getDomain()))
                                        .path("/search/")
                                        .query(queryMatcher(true)
                                                .param("text", not(isEmptyOrNullString()))
                                        )
                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignTaxiTouchV2Export, SignEntry> getSignTaxiTouchV2Checks() {
        return new ExportChecks<SignTaxiTouchV2Export, SignEntry>(
                new SignTaxiTouchV2Export(),
                asList(
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("m.taxi.yandex."))
                                        .query(queryMatcher(true)
                                                .param("utm_term", not(isEmptyOrNullString()))
                                        )
                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host(startsWith("m.taxi.yandex."))
                                        .query(queryMatcher(true)
                                                .param("utm_term", not(isEmptyOrNullString()))
                                        )
                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo)
//                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignTravelTouchV2Export, SignEntry> getSignTravelTouchV2Checks() {
        return new ExportChecks<SignTravelTouchV2Export, SignEntry>(
                new SignTravelTouchV2Export(),
                asList(
                        urlPattern(
                                "url",
                                SignEntry::getUrl,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("m.travel.yandex.ru")
                                        .path("/")
                                        .query(queryMatcher(true)
                                                .param("utm_source", "yandex_sign_mobile")
                                                .param("utm_content", e.getCounter())
                                        )

                        ),
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .scheme("https")
                                        .host("m.travel.yandex.ru")
                                        .query(queryMatcher(true)
                                                .param("utm_source", "yandex_sign_mobile")
                                                .param("utm_content", e.getCounter())
                                        )
                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo)
//                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
        );
    }

    public static ExportChecks<SignVideoV2Export, SignEntry> getSignVideoV2Checks() {
        return new ExportChecks<SignVideoV2Export, SignEntry>(
                new SignVideoV2Export(),
                asList(
                        urlPattern(
                                "urlText",
                                SignEntry::getUrltext,
                                e -> urlMatcher()
                                        .host(startsWith("yandex."))
                                        .path(startsWith("/video"))
                        ),
                        httpResponse("url", SignEntry::getUrl),
                        httpResponse("urlText", SignEntry::getUrltext),
                        TextLengthCheck.textLength("text", SignEntry::getText, e -> TEXT_LENGTH_MATCHER),
                        DomainCheck.domain("url", SignEntry::getUrl, SignEntry::getGeo),
                        DomainCheck.domain("urlText", SignEntry::getUrltext, SignEntry::getGeo),
                        regionTargeting("domain", SignEntry::getDomain, SignEntry::getGeo)
                ),
                regionTranslationsChek("geo", MORDA_LANGUAGES)
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
        for (ExportCheck<?> check : checks) {
            data.add(new Object[]{export.getName(), export, check});
        }

        exportCheck.forEach(e -> data.add(new Object[]{export.getName(), export, e}));
        return data;
    }

    public AbstractMordaExport<T, E> getExport() {
        return export;
    }

    public List<ExportCheck<E>> getChecks() {
        return checks;
    }
}
