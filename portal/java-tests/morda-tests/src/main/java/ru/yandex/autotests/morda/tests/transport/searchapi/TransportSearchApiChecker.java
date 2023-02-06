package ru.yandex.autotests.morda.tests.transport.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class TransportSearchApiChecker {//implements SearchApiChecker {

//    protected TransportSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//    public static TransportSearchApiChecker transportSearchApiChecker(MordaSearchApiVersion version,
//                                                                      GeobaseRegion region,
//                                                                      MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new TransportSearchApiV1Checker(region, language);
//            case V2:
//                return new TransportSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//    @Override
//    @Step("Check Transport")
//    public void check(MordaSearchApiResponse response) {
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getTransport(), notNullValue());
//        assertThat(searchApiResponse.getTransport().getData(), notNullValue());
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiTransportData transport = response.getTransport().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.addAll(transport.getList().stream()
//                .map(e -> SearchApiChecker.getFallbackUrl(e.getUrl()))
//                .collect(toList())
//        );
//
//        return urls;
//    }
//
//    @Override
//    public Set<String> getStaticUrls(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiTransportData transport = response.getTransport().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.addAll(transport.getList().stream()
//                .map(SearchApiTransportItem::getIcon)
//                .collect(toList())
//        );
//
//        return urls;
//    }
}
