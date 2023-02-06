package ru.yandex.autotests.morda.tests.stocks.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class StocksSearchApiChecker {//implements SearchApiChecker {

//    public StocksSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//    public static StocksSearchApiChecker stocksSearchApiChecker(MordaSearchApiVersion version,
//                                                                GeobaseRegion region,
//                                                                MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new StocksSearchApiV1Checker(region, language);
//            case V2:
//                return new StocksSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//    @Override
//    @Step("Check Stocks")
//    public void check(MordaSearchApiResponse response) {
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getStocks(), notNullValue());
//        assertThat(searchApiResponse.getStocks().getData(), notNullValue());
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiStocksData stocks = response.getStocks().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        stocks.getGroups().stream().forEach(group -> {
//            urls.addAll(group.getRows().stream().map(SearchApiStocksRow::getUrl).collect(toList()));
//        });
//
//        return urls;
//    }
}
