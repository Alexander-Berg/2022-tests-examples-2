package ru.yandex.autotests.morda.data.tv;

import org.hamcrest.Matcher;
import ru.yandex.autotests.morda.data.Data;
import ru.yandex.autotests.morda.data.DataWithRegion;
import ru.yandex.autotests.morda.matchers.url.UrlMatcher;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.geobase.regions.GeobaseRegion;

import java.util.regex.Pattern;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static ru.yandex.autotests.morda.matchers.string.RegexMatcher.regex;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/16
 */
public interface TvData extends Data, DataWithRegion {
    String getHost();

    default GeobaseRegion getTvRegion() {
        MordaDomain domain = MordaDomain.fromString(getRegion().getKubrDomain());
        if (domain == MordaDomain.UA || domain == MordaDomain.BY) {
            return new GeobaseRegion(getRegion().getCountryId());
        }
        return getRegion();
    }

    default String getBigHost() {
        return fromUri("https://tv.yandex{domain}/")
                .build(getDomain().getValue())
                .toString();
    }

    default String getTouchHost() {
        return fromUri("https://m.tv.yandex{domain}/")
                .build(getDomain().getValue())
                .toString();
    }

    default String getUrl() {
        return fromUri(getHost())
                .path("{region}")
                .build(getTvRegion().getRegionId())
                .toString();
    }

    default MordaDomain getDomain() {
        return MordaDomain.fromString(getTvRegion().getKubrDomain());
    }

    default UrlMatcher getUrlMatcher() {
        return urlMatcher(getUrl());
    }

    default String getChannelUrl(String channelId) {
        return fromUri(getUrl())
                .path("channels/{channelId}")
                .build(channelId)
                .toString();
    }

    default UrlMatcher getChannelUrlMatcher() {
        return urlMatcher(getHost())
                .path(regex("%s/channels/\\d+", getTvRegion().getRegionId()));
    }

    default UrlMatcher getChannelUrlMatcher(String channelId) {
        return urlMatcher(getChannelUrl(channelId));
    }

    default UrlMatcher getEventUrlMatcher() {
        return urlMatcher(getHost())
                .path(regex("%s/program/\\d+", getTvRegion().getRegionId()))
                .query("eventId", regex("\\d+"));
    }

    default String getEventUrl(String programId, String eventId) {
        return fromUri(getUrl())
                .path("program/{programId}")
                .queryParam("eventId", eventId)
                .build(programId)
                .toString();
    }

    default UrlMatcher getEventUrlMatcher(String programId, String eventId) {
        return urlMatcher(getEventUrl(programId, eventId));
    }

    default Matcher<String> getTimeMatcher() {
        return regex(Pattern.compile("\\d{2}:\\d{2}"));
    }
}
