package ru.yandex.autotests.morda.tests.tv.searchapi;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/08/16
 */
public abstract class TvSearchApiChecker {//implements SearchApiChecker {
//    protected TvData tvData;
//
//    public TvSearchApiChecker(GeobaseRegion region, MordaLanguage language) {
//    }
//
//    public static TvSearchApiChecker tvSearchApiChecker(MordaSearchApiVersion version,
//                                                        GeobaseRegion region,
//                                                        MordaLanguage language) {
//
//        switch (version) {
//            case V1:
//                return new TvSearchApiV1Checker(region, language);
//            case V2:
//                return new TvSearchApiV2Checker(region, language);
//            default:
//                throw new IllegalStateException("Failed to get checker for version " + version);
//        }
//    }
//
//
//    public List<SearchApiTvProgram> getPrograms(SearchApiTvTab tab) {
//        return tab.getProgram().stream()
//                .filter(e -> !"separator".equals(e.getType()))
//                .collect(toList());
//    }
//
//    public SearchApiTvProgram getRandomProgram(SearchApiTvTab tab) {
//        List<SearchApiTvProgram> programs = getPrograms(tab);
//        return programs.get(RANDOM.nextInt(programs.size()));
//    }
//
//    @Override
//    @Step("Check Tv")
//    public void check(MordaSearchApiResponse response) {
//        checkExists(response);
//        checkData(response);
//        checkTvData(response);
//        checkTvTabs(response);
//    }
//
//    @Step("Check Tv Block")
//    public void checkData(MordaSearchApiResponse response) {
//        SearchApiTv tv = response.getTv();
//
//        Matcher<SearchApiTv> tvMatcher = allOfDetailed(
//                hasPropertyWithValue(on(SearchApiTv.class).getTtl(), greaterThan(0)),
//                hasPropertyWithValue(on(SearchApiTv.class).getTtv(), greaterThan(0))
////                hasPropertyWithValue(on(SearchApiTv.class).getTitle(), equalTo(ApiSearch.TV_TITLE.get(tvData.getLanguage().getLanguage())))
//        );
//
//        checkWithAttachment(tv, tvMatcher);
//    }
//
//    @Step("Check Tv Data")
//    public void checkTvData(MordaSearchApiResponse response) {
//        SearchApiTvData searchApiTvData = response.getTv().getData();
//
//        Matcher<SearchApiTvData> tvMatcher = allOfDetailed(
//                SearchApiTvDataMatchers.withGeo(equalTo(tvData.getAfishaRegion().getRegionId())),
//                SearchApiTvDataMatchers.withUrl(tvData.getUrlMatcher())
//        );
//
//        checkWithAttachment(searchApiTvData, tvMatcher);
//    }
//
//    @Step("Check Tv tabs")
//    public void checkTvTabs(MordaSearchApiResponse response) {
//        response.getTv().getData().getTab().forEach(tvTab -> checkTvTab(tvTab.getTitle(), tvTab));
//
//        assertThat("Слишком мало табов ТВ", response.getTv().getData().getTab(), hasSize(greaterThanOrEqualTo(5)));
//    }
//
//    @Step("Check Tv tab: \"{0}\"")
//    public void checkTvTab(String id, SearchApiTvTab tab) {
//        checkWithAttachment(tab, getTabMatcher(tab));
//
//        checkTabEvents(tab);
//    }
//
//    @Step("Check programs")
//    public void checkTabEvents(SearchApiTvTab tab) {
//        Matcher<List<SearchApiTvProgram>> tvProgramsMatcher = hasItemsDetailed(
//                getPrograms(tab).stream()
//                        .map(program -> getProgramMatcher(tab, program))
//                        .collect(Collectors.toList())
//        );
//
//        checkWithAttachment(getPrograms(tab), tvProgramsMatcher);
//    }
//
//    public Matcher<SearchApiTvProgram> getProgramMatcher(SearchApiTvTab tab, SearchApiTvProgram event) {
//        AllOfDetailedMatcher<SearchApiTvProgram> eventMatcher = AllOfDetailedMatcher.allOfDetailed(
//                SearchApiTvProgramMatchers.withTime(tvData.getTimeMatcher()),
//                SearchApiTvProgramMatchers.withTtl(greaterThan(0)),
//                SearchApiTvProgramMatchers.withProgramId(not(isEmptyOrNullString())),
//                SearchApiTvProgramMatchers.withEventId(not(isEmptyOrNullString())),
//                SearchApiTvProgramMatchers.withUrl(tvData.getEventUrlMatcher(event.getProgramId(), event.getEventId())),
//                SearchApiTvProgramMatchers.withTitle(not(isEmptyOrNullString()))
//        );
//
//        if (tab.getType().equals("now") || tab.getType().equals("evening")) {
//            eventMatcher.and(
//                    SearchApiTvProgramMatchers.withChannel(not(isEmptyOrNullString()))
//            );
//        }
//
//        return eventMatcher;
//    }
//
//
//    public Matcher<SearchApiTvTab> getNowTabMatcher() {
//        return allOfDetailed(
////                SearchApiTvTabMatchers.withTitle(equalTo(Tv.TITLE_NOW_API.get(tvData.getLanguage().getLanguage()))),
//                SearchApiTvTabMatchers.withType(equalTo("now")),
//                SearchApiTvTabMatchers.withUrl(tvData.getUrlMatcher())
//        );
//    }
//
//    public Matcher<SearchApiTvTab> getEveningTabMatcher() {
//        return allOfDetailed(
////                SearchApiTvTabMatchers.withTitle(equalTo(Tv.TITLE_EVENING.get(tvData.getLanguage().getLanguage()))),
//                SearchApiTvTabMatchers.withType(equalTo("evening")),
//                SearchApiTvTabMatchers.withUrl(tvData.getUrlMatcher().query("period", "evening"))
//        );
//    }
//
//    public Matcher<SearchApiTvTab> getTabMatcher(SearchApiTvTab tvTab) {
//        if (tvTab.getType().equals("now")) {
//            return getNowTabMatcher();
//        }
//
//        if (tvTab.getType().equals("evening")) {
//            return getEveningTabMatcher();
//        }
//
//        return allOfDetailed(
//                SearchApiTvTabMatchers.withTitle(not(isEmptyOrNullString())),
//                SearchApiTvTabMatchers.withType(equalTo("channel")),
//                SearchApiTvTabMatchers.withUrl(tvData.getChannelUrlMatcher())
//        );
//    }
//
//    @Override
//    public void checkExists(MordaSearchApiResponse searchApiResponse) {
//        assertThat(searchApiResponse, notNullValue());
//        assertThat(searchApiResponse.getTv(), notNullValue());
//        assertThat(searchApiResponse.getTv().getData(), notNullValue());
//    }
//
//    @Override
//    public Set<String> getUrlsToPing(MordaSearchApiResponse searchApiResponse) {
//        checkExists(searchApiResponse);
//
//        Set<String> urls = new HashSet<>();
//        SearchApiTvData tvData = searchApiResponse.getTv().getData();
//        urls.add(tvData.getUrl());
//        tvData.getTab().stream().forEach(tab -> {
//            urls.add(tab.getUrl());
//            urls.add(getRandomProgram(tab).getUrl());
//        });
//
//        return urls;
//    }
}
