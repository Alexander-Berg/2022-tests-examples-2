package ru.yandex.autotests.morda.tests.web.utils;


import ru.yandex.autotests.utils.morda.region.Region;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public enum GeoLocation {
    MSK_SVO(Region.MOSCOW, new GeoCoordinates("55.96931716680345", "37.41953740940979")),
    MSK_DME(Region.DOMODEDOVO, new GeoCoordinates("55.41535430738144", "37.899407206200685")),
    MSK_VKO(Region.VNUKOVO, new GeoCoordinates("55.60123064900301", "37.28039628090828")),
    MSK_CENTER(Region.MOSCOW, new GeoCoordinates("55.74783793380062", "37.565237400882175")),
    SPB_LED(Region.PUSHKIN, new GeoCoordinates("59.79977043604069", "30.2715785887979")),
    SPB_CENTER(Region.SPB, new GeoCoordinates("59.93171079473379", "30.354660039698665")),


    MSK_BELORUSSKIY(Region.MOSCOW, new GeoCoordinates("55.77328716185137", "37.58410200066256")),
    SPB_FONTANKA(Region.SPB, new GeoCoordinates("59.92314595411795", "30.322547817248175")),
    KIEV(Region.KIEV, new GeoCoordinates("50.450097", "30.523397")),
    PERM(Region.PERM, new GeoCoordinates("58.00550063", "56.2456699")),
    NOVOSIBIRSK(Region.NOVOSIBIRSK, new GeoCoordinates("55.02040722693494", "82.93943503639899")),
    MINSK(Region.MINSK, new GeoCoordinates("53.89156869807424", "27.547818463671277")),
    ASTANA(Region.ASTANA, new GeoCoordinates("51.14168269361951", "71.4334735332312")),
    ISTANBUL(Region.ISTANBUL, new GeoCoordinates("41.05073036834944","28.9698424397361"));

    private final Region region;
    private final GeoCoordinates coordinates;

    GeoLocation(Region region, GeoCoordinates coordinates) {
        this.region = region;
        this.coordinates = coordinates;
    }

    public GeoCoordinates getCoordinates() {
        return coordinates;
    }

    public String getGeoId() {
        return region.getRegionId();
    }

    public Region getRegion(){
        return region;
    }
}
