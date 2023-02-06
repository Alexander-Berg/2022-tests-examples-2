package ru.yandex.autotests.morda.data.tv.searchapi;

import ru.yandex.autotests.morda.data.tv.TvTouchData;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.core.UriBuilder;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/09/16
 */
public class TvSearchApiV1Data extends TvSearchApiData implements TvTouchData {

    public TvSearchApiV1Data(GeobaseRegion region) {
        super(region);
    }

    @Override
    public String getUrl() {
        return UriBuilder.fromUri(super.getUrl())
                .queryParam("appsearch_header", "1")
                .build()
                .toString();
    }
}
