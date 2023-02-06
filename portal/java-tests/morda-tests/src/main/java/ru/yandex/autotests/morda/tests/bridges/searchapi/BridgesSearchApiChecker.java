package ru.yandex.autotests.morda.tests.bridges.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class BridgesSearchApiChecker {//implements SearchApiChecker {
//
//    protected BridgesSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//    public static BridgesSearchApiChecker bridgesSearchApiChecker(MordaSearchApiVersion version,
//                                                                  GeobaseRegion region,
//                                                                  MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new BridgesSearchApiV1Checker(region, language);
//            case V2:
//                return new BridgesSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//    @Override
//    @Step("Check Bridges")
//    public void check(MordaSearchApiResponse response) {
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getBridges(), notNullValue());
//        assertThat(searchApiResponse.getBridges().getData(), notNullValue());
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiBridgesData bridges = response.getBridges().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.addAll(bridges.get0().stream().map(SearchApiBridgesItem::getUrl).collect(toList()));
//        urls.addAll(bridges.get1().stream().map(SearchApiBridgesItem::getUrl).collect(toList()));
//
//        return urls;
//    }
}
