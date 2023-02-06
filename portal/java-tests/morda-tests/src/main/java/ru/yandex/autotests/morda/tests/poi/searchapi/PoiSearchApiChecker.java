package ru.yandex.autotests.morda.tests.poi.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class PoiSearchApiChecker {//implements SearchApiChecker {

//    public PoiSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//    public static PoiSearchApiChecker poiSearchApiChecker(MordaSearchApiVersion version,
//                                                          GeobaseRegion region,
//                                                          MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new PoiSearchApiV1Checker(region, language);
//            case V2:
//                return new PoiSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//    @Override
//    @Step("Check Poi")
//    public void check(MordaSearchApiResponse response) {
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getPoi(), notNullValue());
//        assertThat(searchApiResponse.getPoi().getData(), notNullValue());
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse response) {
//        SearchApiPoiData poi = response.getPoi().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.add(getFallbackUrl(poi.getUrl()));
//        urls.addAll(poi.getGroups().stream()
//                .map(e -> getFallbackUrl(e.getUrl()))
//                .collect(toList())
//        );
//
//        return urls;
//    }
//
//    @Override
//    public Set<String> getStaticUrls(MordaSearchApiResponse response) {
//        SearchApiPoiData poi = response.getPoi().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.add(poi.getMapUrl());
//        urls.addAll(poi.getGroups().stream()
//                .map(SearchApiPoiGroup::getIcon)
//                .collect(toList())
//        );
//
//        return urls;
//    }
}
