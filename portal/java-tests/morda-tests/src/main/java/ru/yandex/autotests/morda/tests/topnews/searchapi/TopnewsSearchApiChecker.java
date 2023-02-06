package ru.yandex.autotests.morda.tests.topnews.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class TopnewsSearchApiChecker {//implements SearchApiChecker {
//
//    public TopnewsSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//    public static TopnewsSearchApiChecker topnewsSearchApiChecker(MordaSearchApiVersion version,
//                                                                  GeobaseRegion region,
//                                                                  MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new TopnewsSearchApiV1Checker(region, language);
//            case V2:
//                return new TopnewsSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//    @Override
//    @Step("Check Topnews")
//    public void check(MordaSearchApiResponse response) {
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getTopnews(), notNullValue());
//        assertThat(searchApiResponse.getTopnews().getData(), notNullValue());
//    }
//
//    public SearchApiTopnewsItem getRandomItem(SearchApiTopnewsTab tab) {
//        return tab.getNews().get(RANDOM.nextInt(tab.getNews().size()));
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiTopnewsData topnews = response.getTopnews().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.add(topnews.getUrl());
//
//        topnews.getTab().forEach(tab -> {
//            urls.add(tab.getUrl());
//            urls.add(getRandomItem(tab).getUrl());
//        });
//
//        return urls;
//    }
}
