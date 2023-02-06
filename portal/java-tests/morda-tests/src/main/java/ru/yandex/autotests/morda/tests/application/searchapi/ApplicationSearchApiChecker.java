package ru.yandex.autotests.morda.tests.application.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class ApplicationSearchApiChecker { //implements SearchApiChecker {

//    protected ApplicationSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//
//    public static ApplicationSearchApiChecker applicationSearchApiChecker(MordaSearchApiVersion version,
//                                                                          GeobaseRegion region,
//                                                                          MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new ApplicationSearchApiV1Checker(region, language);
//            case V2:
//                return new ApplicationSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//    @Override
//    @Step("Check Application")
//    public void check(MordaSearchApiResponse response) {
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getApplication(), notNullValue());
//        assertThat(searchApiResponse.getApplication().getData(), notNullValue());
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiApplicationData application = response.getApplication().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.addAll(application.getList().stream().map(SearchApiApplicationItem::getUrl).collect(toList()));
//
//        return urls;
//    }
//
//    @Override
//    public Set<String> getStaticUrls(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiApplicationData application = response.getApplication().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.addAll(application.getList().stream().map(SearchApiApplicationItem::getIcon).collect(toList()));
//
//        return urls;
//    }
}
