package ru.yandex.autotests.morda.tests.informer.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class InformerSearchApiChecker {//implements SearchApiChecker {
//
//    protected InformerSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//    public static InformerSearchApiChecker informerSearchApiChecker(MordaSearchApiVersion version,
//                                                                    GeobaseRegion region,
//                                                                    MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new InformerSearchApiV1Checker(region, language);
//            case V2:
//                return new InformerSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//    @Override
//    @Step("Check Informer")
//    public void check(MordaSearchApiResponse response) {
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getInformer(), notNullValue());
//        assertThat(searchApiResponse.getInformer().getData(), notNullValue());
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiInformerData informer = response.getInformer().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.add(informer.getTraffic().getUrl());
//        urls.add(informer.getTraffic().getApps().getMaps().getUrl());
//        urls.add(informer.getTraffic().getApps().getNavigator().getUrl());
//
//        List<SearchApiInformerItem> informerItems = new ArrayList<>();
//        informerItems.addAll(informer.getList());
//        informerItems.addAll(informer.getMore().getList());
//
//        urls.addAll(informerItems.stream()
//                .filter(e -> e != null && e.getUrl() != null && !e.getUrl().startsWith("viewport"))
//                .map(e -> getFallbackUrl(e.getUrl()))
//                .collect(toList())
//        );
//
//        return urls;
//    }
//
//    @Override
//    public Set<String> getStaticUrls(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiInformerData informer = response.getInformer().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.add(informer.getTraffic().getIcon());
//        urls.add(informer.getTraffic().getMapUrl());
//
//        urls.add(informer.getMore().getIcon());
//
//        List<SearchApiInformerItem> informerItems = new ArrayList<>();
//        informerItems.addAll(informer.getList());
//        informerItems.addAll(informer.getMore().getList());
//
//        urls.addAll(informerItems.stream()
//                .map(SearchApiInformerItem::getIcon)
//                .collect(toList())
//        );
//
//        return urls;
//    }
}
