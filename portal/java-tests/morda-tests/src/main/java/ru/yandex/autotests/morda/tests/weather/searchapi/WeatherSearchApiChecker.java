package ru.yandex.autotests.morda.tests.weather.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class WeatherSearchApiChecker {//implements SearchApiChecker {
//
//    protected WeatherSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//    public static WeatherSearchApiChecker weatherSearchApiChecker(MordaSearchApiVersion version,
//                                                                  GeobaseRegion region,
//                                                                  MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new WeatherSearchApiV1Checker(region, language);
//            case V2:
//                return new WeatherSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//
//    @Override
//    @Step("Check Weather")
//    public void check(MordaSearchApiResponse response) {
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getWeather(), notNullValue());
//        assertThat(searchApiResponse.getWeather().getData(), notNullValue());
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiWeatherData weather = response.getWeather().getData();
//
//        Set<String> urls = new HashSet<>();
//
//        urls.add(SearchApiChecker.getYellowskinkUrl(weather.getUrl()));
//        urls.add(SearchApiChecker.getYellowskinkUrl(weather.getUrlV5()));
//        urls.add(SearchApiChecker.getYellowskinkUrl(weather.getNowUrl()));
//        urls.add(SearchApiChecker.getYellowskinkUrl(weather.getNoticeUrl()));
//
//        urls.addAll(weather.getForecast().stream()
//                .map(e -> SearchApiChecker.getYellowskinkUrl(e.getUrl()))
//                .collect(toList())
//        );
//
//        urls.addAll(weather.getShortForecast().stream()
//                .map(e -> SearchApiChecker.getYellowskinkUrl(e.getUrl()))
//                .collect(toList())
//        );
//
//        urls.addAll(weather.getParts().stream()
//                .map(e -> SearchApiChecker.getYellowskinkUrl(e.getUrl()))
//                .collect(toList())
//        );
//
//        return urls;
//    }
//
//    @Override
//    public Set<String> getStaticUrls(MordaSearchApiResponse response) {
//        checkExists(response);
//        SearchApiWeatherData weather = response.getWeather().getData();
//
//        Set<String> urls = new HashSet<>();
//        urls.add(weather.getIcon());
//
//        weather.getForecast().forEach(e -> {
//            urls.add(e.getIcon());
//            urls.add(e.getIconDaynight());
//        });
//
//        weather.getShortForecast().forEach(e -> {
//            urls.add(e.getIcon());
//            urls.add(e.getIconDaynight());
//        });
//
//        weather.getParts().forEach(e -> {
//            urls.add(e.getIcon());
//            urls.add(e.getIconDaynight());
//        });
//
//        return urls;
//    }
}
