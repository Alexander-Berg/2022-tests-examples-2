package ru.yandex.autotests.morda.data.afisha;

import ru.yandex.autotests.morda.beans.exports.afisha_geo_v2.AfishaGeoV2Entry;
import ru.yandex.autotests.morda.beans.exports.afisha_geo_v2.AfishaGeoV2Export;
import ru.yandex.autotests.morda.exports.filters.MordaDomainFilter;
import ru.yandex.autotests.morda.exports.filters.MordaGeoFilter;
import ru.yandex.autotests.morda.exports.filters.MordaLanguageFilter;
import ru.yandex.autotests.morda.matchers.url.UrlMatcher;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.geobase.Language;
import ru.yandex.geobase.regions.GeobaseRegion;

import java.util.List;
import java.util.regex.Pattern;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static ru.yandex.autotests.morda.matchers.string.RegexMatcher.regex;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/16
 */
public interface AfishaBlockData {
    AfishaGeoV2Export AFISHA_GEO_V2_EXPORT = new AfishaGeoV2Export().populate();

    static GeobaseRegion getAfishaRegion(GeobaseRegion region, MordaLanguage language) {

        List<AfishaGeoV2Entry> entries = AFISHA_GEO_V2_EXPORT.find(
                MordaDomainFilter.filter(MordaDomain.fromString(region.getKubrDomain())),
                MordaGeoFilter.filter(region),
                MordaLanguageFilter.filter(language)
        );

        assertThat("Failed to get data from export afisha_geo_v2", entries, hasSize(lessThanOrEqualTo(1)));

        if (entries.size() == 1) {
            return new GeobaseRegion(entries.get(0).getShowGeo());
        }

        return region;
    }

    static String getHost(GeobaseRegion region, MordaLanguage language) {
        return fromUri("https://afisha.yandex{domain}/")
                .build(getDomain(region, language).getValue())
                .toString();
    }

    static MordaDomain getDomain(GeobaseRegion region, MordaLanguage language) {
        return MordaDomain.fromString(getAfishaRegion(region, language).getKubrDomain());
    }

    default UrlMatcher getUrlMatcher(GeobaseRegion region, MordaLanguage language) {
        GeobaseRegion afishaRegion = getAfishaRegion(region, language);

        return urlMatcher(getHost(region, language))
                .query("utm_medium", "yamain_afisha");
//                .query("city", afishaRegion.getTranslations(HttpGeobase.Language.EN).getNominativeCase().toLowerCase());
    }

    default UrlMatcher getEventUrlMatcher(GeobaseRegion region, MordaLanguage language, String eventId) {
        GeobaseRegion afishaRegion = getAfishaRegion(region, language);

        return urlMatcher(getHost(region, language))
                .path("events/" + eventId)
                .query("utm_medium", "yamain_afisha")
                .query("city", afishaRegion.getTranslations(Language.EN).getNominativeCase().toLowerCase());
    }

    default UrlMatcher getPosterUrlMatcher(AfishaPosterSize afishaPosterSize) {
        return urlMatcher("https://avatars.mds.yandex.net/")
                .path(regex(Pattern.compile("get-afishanew/\\d+/\\w+/" + afishaPosterSize.getValue())));
    }

    enum AfishaPosterSize {
        _100x143_noncrop("100x143_noncrop"),
        _200x286_noncrop("200x286_noncrop"),
        _300x429_noncrop("300x429_noncrop"),
        _960x960_noncrop("960x690_noncrop");

        private String value;

        AfishaPosterSize(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }
}
