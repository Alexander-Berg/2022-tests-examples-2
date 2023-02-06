package ru.yandex.autotests.morda.data.tv.searchapi;

import ru.yandex.autotests.morda.data.tv.TvData;
import ru.yandex.geobase.regions.GeobaseRegion;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/09/16
 */
public abstract class TvSearchApiData implements TvData {

    private GeobaseRegion region;

    public TvSearchApiData(GeobaseRegion region) {
        this.region = region;
    }

    @Override
    public GeobaseRegion getRegion() {
        return region;
    }
}
