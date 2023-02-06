package ru.yandex.autotests.morda.tests.now.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class NowSearchApiChecker {//implements SearchApiChecker {

//    public NowSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//    public static NowSearchApiChecker nowSearchApiChecker(MordaSearchApiVersion version,
//                                                          GeobaseRegion region,
//                                                          MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new NowSearchApiV1Checker(region, language);
//            case V2:
//                return new NowSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//    @Override
//    @Step("Check Now")
//    public void check(MordaSearchApiResponse response) {
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getNow(), notNullValue());
//        assertThat(searchApiResponse.getNow().getData(), notNullValue());
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiNow now = response.getNow();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.addAll(now.getData().getSpecial().stream()
//                .map(SearchApiNowSpecial::getUrl)
//                .collect(toList())
//        );
//
//        return urls;
//    }
//
//    @Override
//    public Set<String> getStaticUrls(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiNow now = response.getNow();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.add(now.getData().getImageId());
//        urls.addAll(now.getData().getSpecial().stream()
//                .map(SearchApiNowSpecial::getImageId)
//                .collect(toList())
//        );
//
//        return urls;
//    }
}
